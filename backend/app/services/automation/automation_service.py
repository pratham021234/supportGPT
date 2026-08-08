import logging
import asyncio
import httpx
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.repositories.automation_repo import (
    automation_rule_repo, workflow_execution_repo, webhook_endpoint_repo,
    WorkflowExecutionInternalCreate, ExecutionStatus
)
from app.repositories.ticket_repo import ticket_repo, TicketInternalCreate
from app.repositories.conversation_repo import conversation_repo, MessageInternalCreate, message_repo
from app.models.notification import SystemEvent
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

class ConditionEngine:
    def evaluate(self, payload: Dict[str, Any], conditions: List[Dict[str, Any]]) -> bool:
        if not conditions:
            return True
            
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            target_value = condition.get("value")
            
            actual_value = payload.get(field)
            
            if actual_value is None:
                return False
                
            if operator == "equals" or operator == "eq":
                if actual_value != target_value: return False
            elif operator == "not_equals" or operator == "neq":
                if actual_value == target_value: return False
            elif operator == "lt" or operator == "less_than":
                try:
                    if float(actual_value) >= float(target_value): return False
                except:
                    return False
            elif operator == "gt" or operator == "greater_than":
                try:
                    if float(actual_value) <= float(target_value): return False
                except:
                    return False
            elif operator == "contains":
                if str(target_value).lower() not in str(actual_value).lower(): return False
            else:
                return False
                
        return True

class ActionEngine:
    async def execute(self, db: AsyncSession, workspace_id: str, payload: Dict[str, Any], actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logs = []
        for action in actions:
            action_type = action.get("type")
            action_payload = action.get("payload", {})
            
            log_entry = {"action": action_type, "timestamp": datetime.utcnow().isoformat(), "status": "PENDING"}
            
            try:
                if action_type == "CREATE_TICKET":
                    title = action_payload.get("title", f"Automated Ticket from {payload.get('event_type', 'System')}")
                    description = action_payload.get("description", str(payload))
                    priority = action_payload.get("priority", "MEDIUM")
                    
                    # Assuming we know customer_id from payload, else None
                    customer_id = payload.get("customer_id")
                    if customer_id:
                        ticket_in = TicketInternalCreate(
                            workspace_id=workspace_id,
                            customer_id=customer_id,
                            title=title,
                            description=description
                        )
                        # Ignoring priority enum for simple mock
                        await ticket_repo.create(db, obj_in=ticket_in)
                        
                elif action_type == "SEND_EMAIL":
                    to_email = action_payload.get("to")
                    subject = action_payload.get("subject", "Automated Alert")
                    body = action_payload.get("body", str(payload))
                    if to_email:
                        await email_service.send_email(to_email, subject, body)
                        
                elif action_type == "SEND_WEBHOOK":
                    # Fire-and-forget webhook
                    endpoints = await webhook_endpoint_repo.get_active_by_workspace(db, workspace_id)
                    for endpoint in endpoints:
                        # In production this would be queued in Celery
                        asyncio.create_task(self._send_webhook(endpoint.url, payload))
                
                log_entry["status"] = "SUCCESS"
            except Exception as e:
                log_entry["status"] = "FAILED"
                log_entry["error"] = str(e)
                
            logs.append(log_entry)
            
        return logs
        
    async def _send_webhook(self, url: str, payload: Dict[str, Any]):
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=payload, timeout=5.0)
            except Exception as e:
                logger.error(f"Webhook delivery failed: {e}")

class AutomationEngine:
    def __init__(self):
        self.condition_engine = ConditionEngine()
        self.action_engine = ActionEngine()
        
    async def process_event(self, db: AsyncSession, event: SystemEvent):
        """Called asynchronously by the EventBus when a new SystemEvent is published."""
        
        rules = await automation_rule_repo.get_active_by_trigger(db, event.event_type)
        if not rules:
            return
            
        payload = event.payload or {}
        payload["event_type"] = event.event_type
        payload["entity_id"] = str(event.entity_id) if event.entity_id else None
        
        for rule in rules:
            if str(rule.workspace_id) != str(event.workspace_id):
                continue
                
            # 1. Check Conditions
            if self.condition_engine.evaluate(payload, rule.conditions):
                # 2. Execute Actions
                logs = await self.action_engine.execute(db, str(rule.workspace_id), payload, rule.actions)
                
                # 3. Record Execution
                has_failures = any(l.get("status") == "FAILED" for l in logs)
                status = ExecutionStatus.FAILED if has_failures else ExecutionStatus.SUCCESS
                
                exec_in = WorkflowExecutionInternalCreate(
                    workspace_id=str(rule.workspace_id),
                    rule_id=str(rule.id),
                    event_id=str(event.id),
                    status=status,
                    execution_logs=logs,
                    error_message="Action failed" if has_failures else None
                )
                await workflow_execution_repo.create(db, obj_in=exec_in)

automation_engine = AutomationEngine()
