import logging
from typing import Dict, Any, List
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import SenderType, ConversationStatus
from app.services.messaging.websocket_manager import websocket_manager
from app.services.messaging.conversation_engine import conversation_engine
from app.services.messaging.message_service import message_service
from app.services.agent.testing_service import agent_testing_service
from app.services.handoff.escalation_engine import escalation_engine
from app.services.agent.agent_router import agent_router
from app.repositories.conversation_repo import conversation_repo

logger = logging.getLogger(__name__)

class RealtimeMessagingService:
    async def handle_customer_message(self, db: AsyncSession, websocket: WebSocket, conversation_id: str, text: str, user_id: str):
        """
        Receives a message from the customer over WS, stores it,
        triggers the RAG Engine for the agent, and streams the reply back.
        """
        # 1. Store Customer Message
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            await websocket.send_json({"type": "error", "content": "Conversation not found"})
            return
            
        await message_service.store_message(
            db=db,
            conversation_id=conversation_id,
            sender_type=SenderType.CUSTOMER,
            content=text,
            sender_id=str(conv.customer_id)
        )
        
        # Echo back for confirmation via new WebSocketManager
        await websocket_manager.broadcast_to_channel("chat", conversation_id, {
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
                    conv = await conversation_engine.update_conversation(db, conversation_id, {"agent_id": str(best_agent.id)})
            
            if not conv.agent_id:
                await websocket_manager.broadcast_to_channel("chat", conversation_id, {"type": "system_event", "content": "No AI agents available."})
                return
                
            await websocket_manager.broadcast_to_channel("chat", conversation_id, {
                "type": "agent_typing",
                "status": True
            })
            
            try:
                result = await agent_testing_service.test_agent(
                    db=db,
                    agent_id=str(conv.agent_id),
                    query=text,
                    user_id=user_id
                )
                
                ai_text = result.get("answer", "I could not generate an answer.")
                confidence = result.get("confidence_score", 0.0)
                sources = result.get("sources", [])
                
                # Check Escalation Engine FIRST before returning final message
                escalated = False
                escalate_flag = result.get("escalate", False)
                if escalate_flag or confidence < 70.0:
                    escalated = await escalation_engine.evaluate_escalation(
                        db=db, 
                        conversation=conv, 
                        confidence_score=confidence
                    )
                
                # Store AI message
                await message_service.store_message(
                    db=db,
                    conversation_id=conversation_id,
                    sender_type=SenderType.AI_AGENT,
                    content=ai_text,
                    sender_id=str(conv.agent_id),
                    confidence=confidence,
                    sources=sources
                )
                
                # Stream the reply chunks
                words = ai_text.split(" ")
                for word in words:
                    await websocket_manager.broadcast_to_channel("chat", conversation_id, {
                        "type": "token",
                        "content": word + " "
                    })
                    
                await websocket_manager.broadcast_to_channel("chat", conversation_id, {
                    "type": "message_complete",
                    "sender": "AI_AGENT"
                })
                
                if escalated:
                    await websocket_manager.broadcast_to_channel("chat", conversation_id, {
                        "type": "system_event",
                        "content": "Connecting you to a human agent..."
                    })
                
            except Exception as e:
                logger.error(f"RAG Error: {e}")
                await websocket_manager.broadcast_to_channel("chat", conversation_id, {
                    "type": "error",
                    "content": "An error occurred while generating the response."
                })
            finally:
                await websocket_manager.broadcast_to_channel("chat", conversation_id, {
                    "type": "agent_typing",
                    "status": False
                })

    async def handle_agent_message(self, db: AsyncSession, conversation_id: str, text: str, user_id: str):
        """
        Receives a message from a human agent, stores it, and broadcasts it.
        """
        conv = await conversation_repo.get(db, id=conversation_id)
        if not conv:
            return
            
        await message_service.store_message(
            db=db,
            conversation_id=conversation_id,
            sender_type=SenderType.SUPPORT_AGENT,
            content=text,
            sender_id=user_id
        )
        
        await websocket_manager.broadcast_to_channel("chat", conversation_id, {
            "type": "message",
            "sender": "SUPPORT_AGENT",
            "content": text
        })

realtime_messaging_service = RealtimeMessagingService()
