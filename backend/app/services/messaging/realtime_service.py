import json
import logging
from typing import Dict, Any, List
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import SenderType
from app.services.messaging.conversation_service import conversation_service
from app.services.agent.testing_service import agent_testing_service
from app.services.ticketing.ticket_service import ticket_service
from app.services.handoff.handoff_service import handoff_service
from app.services.agent.agent_router import agent_router
from app.models.conversation import ConversationStatus

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps conversation_id -> List of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def broadcast_to_conversation(self, conversation_id: str, message: dict):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to websocket: {e}")

class RealtimeMessagingService:
    def __init__(self):
        self.manager = ConnectionManager()
        
    async def handle_customer_message(self, db: AsyncSession, websocket: WebSocket, conversation_id: str, text: str, user_id: str):
        """
        Receives a message from the customer over WS, stores it,
        triggers the RAG Engine for the agent, and streams the reply back.
        """
        # 1. Store Customer Message
        conv = await conversation_service.get_conversation(db, conversation_id)
        if not conv:
            await websocket.send_json({"type": "error", "content": "Conversation not found"})
            return
            
        await conversation_service.add_message(
            db=db,
            conversation_id=conversation_id,
            sender_type=SenderType.CUSTOMER,
            content=text,
            sender_id=str(conv.customer_id)
        )
        
        # Echo back for confirmation
        await self.manager.broadcast_to_conversation(conversation_id, {
            "type": "message_ack",
            "sender": "CUSTOMER",
            "content": text
        })
        
        # 2. Trigger RAG if agent assigned AND human is not active
        if not conv.is_human_active:
            # Dynamically route if agent is not assigned
            if not conv.agent_id:
                best_agent = await agent_router.route_query(db, str(conv.workspace_id), text)
                if best_agent:
                    conv = await conversation_service.assign_conversation(db, conversation_id, str(best_agent.id))
            
            if not conv.agent_id:
                await websocket.send_json({"type": "system_event", "content": "No AI agents available."})
                return
                
            await self.manager.broadcast_to_conversation(conversation_id, {
                "type": "agent_typing",
                "status": True
            })
            
            try:
                # We'd typically use `agent_testing_service` to run the agent pipeline.
                # However, the async generator in `rag_service` would be more optimal for WS.
                # For MVP, we will use the test service which returns the full result,
                # then simulate a stream back to the socket.
                
                result = await agent_testing_service.test_agent(
                    db=db,
                    agent_id=str(conv.agent_id),
                    query=text,
                    user_id=user_id # the agent's workspace owner for auth
                )
                
                # Store AI message
                ai_text = result.get("answer", "I could not generate an answer.")
                
                await conversation_service.add_message(
                    db=db,
                    conversation_id=conversation_id,
                    sender_type=SenderType.AI_AGENT,
                    content=ai_text,
                    sender_id=str(conv.agent_id)
                )
                
                # Stream the reply (chunking it artificially for the UX)
                # In a true streaming setup we'd await `astream_events` from LangGraph.
                words = ai_text.split(" ")
                for word in words:
                    await self.manager.broadcast_to_conversation(conversation_id, {
                        "type": "token",
                        "content": word + " "
                    })
                    
                await self.manager.broadcast_to_conversation(conversation_id, {
                    "type": "message_complete",
                    "sender": "AI_AGENT"
                })
                
                # Check for Escalation
                escalate = result.get("escalate", False)
                if escalate:
                    logger.info(f"Escalation triggered for conversation {conversation_id}.")
                    
                    # 1. Update status to ESCALATED
                    await conversation_service.update_status(db, conversation_id, ConversationStatus.ESCALATED)
                    
                    # 2. Initiate Handoff (pauses AI after a human accepts, but we'll also pause it now just in case)
                    await handoff_service.initiate_handoff(
                        db=db,
                        conversation_id=conversation_id,
                        from_agent_id=str(conv.agent_id),
                        to_user_id=None,
                        reason=f"AI Confidence Score: {result.get('confidence_score', 0.0)}",
                        initiated_by="AI_SYSTEM"
                    )
                    
                    # 3. Create Ticket
                    await ticket_service.create_ai_escalation(
                        db=db,
                        workspace_id=str(conv.workspace_id),
                        conversation_id=conversation_id,
                        customer_id=str(conv.customer_id),
                        reason=f"AI Escalation triggered. Last query: {text}"
                    )
                    
                    # 4. Broadcast Escalation Event
                    await self.manager.broadcast_to_conversation(conversation_id, {
                        "type": "system_event",
                        "content": "Connecting you to a human agent..."
                    })
                
            except Exception as e:
                logger.error(f"RAG Error: {e}")
                await self.manager.broadcast_to_conversation(conversation_id, {
                    "type": "error",
                    "content": "An error occurred while generating the response."
                })
            finally:
                await self.manager.broadcast_to_conversation(conversation_id, {
                    "type": "agent_typing",
                    "status": False
                })

realtime_messaging_service = RealtimeMessagingService()
