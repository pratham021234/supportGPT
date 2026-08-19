import logging
import json
from typing import Dict, Any, AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import time

from app.services.rag.state import RAGState
from app.services.rag.graph import build_rag_graph
from app.services.vector.search_service import search_service
from app.repositories.rag_repo import (
    query_log_repo, answer_log_repo, retrieval_log_repo,
    citation_log_repo, escalation_event_repo,
    QueryLogInternalCreate, AnswerLogInternalCreate,
    RetrievalLogInternalCreate, CitationLogInternalCreate,
    EscalationEventInternalCreate, EscalationStatus
)

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.injection_keywords = [
            "ignore previous instructions", "ignore all previous instructions", 
            "system prompt", "jailbreak", "you are now", "forget your instructions",
            "DAN", "bypass"
        ]

    def _check_prompt_injection(self, query: str):
        query_lower = query.lower()
        for kw in self.injection_keywords:
            if kw in query_lower:
                raise ValueError(f"Security Policy Violation: Prompt injection attempt detected ({kw}).")

    def _get_retrieval_node(self, db: AsyncSession):
        """Creates a closure for the retrieval node that has access to the db session."""
        from app.services.rag.retrieval_engine import retrieval_engine
        
        async def retrieval_node(state: RAGState) -> Dict[str, Any]:
            results = await retrieval_engine.retrieve(
                db=db,
                workspace_id=state.workspace_id,
                user_id=state.user_id,
                query=state.query,
                keywords=state.keywords,
                limit=10,
                agent_routing=state.agent_routing
            )
            return {"retrieved_chunks": results}
        return retrieval_node

    async def _log_execution(self, db: AsyncSession, state: RAGState):
        """Logs the entire graph execution to the database."""
        # 1. Log Query
        query_in = QueryLogInternalCreate(
            workspace_id=state.workspace_id,
            user_id=state.user_id,
            query=state.query,
            language=state.language,
            query_type=state.query_type,
            latency_ms=state.latency_ms
        )
        query_log = await query_log_repo.create(db, obj_in=query_in)

        # 2. Log Answer
        answer_in = AnswerLogInternalCreate(
            query_id=str(query_log.id),
            workspace_id=state.workspace_id,
            answer_text=state.answer,
            confidence_score=state.confidence_score
        )
        answer_log = await answer_log_repo.create(db, obj_in=answer_in)

        # 3. Log Retrieval
        for chunk in state.retrieved_chunks:
            retrieval_in = RetrievalLogInternalCreate(
                query_id=str(query_log.id),
                chunk_id=chunk.get("payload", {}).get("chunk_id"),
                similarity_score=chunk.get("score", 0.0)
            )
            await retrieval_log_repo.create(db, obj_in=retrieval_in)

        # 4. Log Citations
        if hasattr(state, 'citations') and state.citations:
            for cit in state.citations:
                cit_in = CitationLogInternalCreate(
                    answer_id=str(answer_log.id),
                    chunk_id=cit.chunk_id,
                    claim_text=cit.claim
                )
                await citation_log_repo.create(db, obj_in=cit_in)

        # 5. Log Escalation
        from app.services.analytics.analytics_service import analytics_event_service, knowledge_gap_service
        
        await analytics_event_service.log_event(
            db=db,
            workspace_id=str(state.workspace_id),
            event_type="RAG_QUERY",
            metadata_={"confidence_score": state.confidence_score, "latency_ms": state.latency_ms}
        )
        
        if state.escalate:
            esc_in = EscalationEventInternalCreate(
                workspace_id=state.workspace_id,
                query_id=str(query_log.id),
                confidence_score=state.confidence_score,
                status=EscalationStatus.PENDING
            )
            await escalation_event_repo.create(db, obj_in=esc_in)
            
            await analytics_event_service.log_event(
                db=db,
                workspace_id=str(state.workspace_id),
                event_type="AI_ESCALATION",
                metadata_={"confidence_score": state.confidence_score}
            )
            
            await knowledge_gap_service.process_failed_query(
                db=db,
                workspace_id=str(state.workspace_id),
                query=state.query,
                confidence=state.confidence_score
            )

    async def execute_query(self, db: AsyncSession, workspace_id: str, user_id: Optional[str], query: str) -> Dict[str, Any]:
        """Runs the LangGraph synchronously for the query."""
        self._check_prompt_injection(query)
        start_time = time.time()
        
        # Build graph with DB session
        retrieval_node = self._get_retrieval_node(db)
        app = build_rag_graph(retrieval_node)
        
        # Initialize state
        initial_state = RAGState(
            workspace_id=workspace_id,
            user_id=user_id,
            query=query
        )
        
        # Run graph
        result = await app.ainvoke(initial_state.model_dump())
        
        # Finalize state
        final_state = RAGState(**result)
        final_state.latency_ms = int((time.time() - start_time) * 1000)
        
        # Log to DB
        await self._log_execution(db, final_state)
        
        from app.services.rag.response_formatter import response_formatter
        return response_formatter.format_final_response(final_state.model_dump())

    async def stream_query(self, db: AsyncSession, workspace_id: str, user_id: Optional[str], query: str) -> AsyncGenerator[str, None]:
        """Streams LangGraph execution events via Server-Sent Events (SSE)."""
        try:
            self._check_prompt_injection(query)
        except ValueError as e:
            yield f"data: {json.dumps({'event': 'ERROR', 'data': {'error': str(e)}})}\n\n"
            yield "data: [DONE]\n\n"
            return
            
        start_time = time.time()
        
        retrieval_node = self._get_retrieval_node(db)
        app = build_rag_graph(retrieval_node)
        
        import asyncio
        queue = asyncio.Queue()
        
        async def streaming_callback(event: Dict[str, Any]):
            await queue.put(event)
            
        initial_state = RAGState(
            workspace_id=workspace_id,
            user_id=user_id,
            query=query,
            metadata={"streaming_callback": streaming_callback}
        )
        
        # Run graph in background task
        async def run_graph():
            try:
                final_state = None
                async for output in app.astream(initial_state.model_dump()):
                    for node_name, state_update in output.items():
                        await queue.put({
                            "event": node_name,
                            "data": state_update
                        })
                        final_state = state_update
                # End of graph marker
                await queue.put({"event": "DONE", "data": {}})
            except Exception as e:
                logger.error(f"Graph execution failed: {e}")
                await queue.put({"event": "ERROR", "data": {"error": str(e)}})
                await queue.put({"event": "DONE", "data": {}})

        task = asyncio.create_task(run_graph())
        
        while True:
            item = await queue.get()
            event_name = item.get("event")
            
            if event_name == "DONE":
                break
                
            if event_name == "ERROR":
                yield f"data: {json.dumps(item)}\n\n"
                break
                
            if event_name == "generation_chunk":
                yield f"data: {json.dumps(item)}\n\n"
                continue
                
            # Node level events
            data = item.get("data", {})
            event_data = {
                "event": event_name,
                "data": {}
            }
            
            if event_name == "retrieval":
                event_data["data"]["chunks_retrieved"] = len(data.get("retrieved_chunks", []))
            elif event_name == "generation":
                # We already streamed chunks, but we can emit final answer object if needed
                event_data["data"]["answer_complete"] = True
            elif event_name == "validation":
                event_data["data"]["confidence_score"] = data.get("confidence_score")
                event_data["data"]["escalate"] = data.get("escalate")
                
            yield f"data: {json.dumps(event_data)}\n\n"
            
        yield "data: [DONE]\n\n"

rag_service = RAGService()
