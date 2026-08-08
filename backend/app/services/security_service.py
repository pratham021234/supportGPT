import os
import binascii
import hashlib
import json
from typing import Tuple, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.repositories.security_repo import (
    api_key_repo, security_alert_repo,
    ApiKeyInternalCreate, SecurityAlertInternalCreate, AlertSeverity
)
from app.repositories.session_repo import user_session_repo
from app.repositories.ticket_repo import ticket_repo
from app.repositories.user_repo import user_repo

def generate_api_key(prefix: str = "sgpt") -> Tuple[str, str, str]:
    """Generates a raw key, a hashed version for DB, and the prefix."""
    raw_bytes = os.urandom(32)
    raw_key = f"{prefix}_{binascii.hexlify(raw_bytes).decode('utf-8')}"
    
    # Hash it for storage
    key_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()
    
    return raw_key, key_hash, prefix

class ApiKeyService:
    async def create_key(self, db: AsyncSession, workspace_id: str, user_id: str, name: str, scopes: List[str]) -> Tuple[Any, str]:
        raw_key, key_hash, prefix = generate_api_key()
        
        key_in = ApiKeyInternalCreate(
            workspace_id=workspace_id,
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            scopes=scopes
        )
        db_key = await api_key_repo.create(db, obj_in=key_in)
        return db_key, raw_key

    async def get_by_workspace(self, db: AsyncSession, workspace_id: str) -> List[Any]:
        return await api_key_repo.get_by_workspace(db, workspace_id)

    async def revoke_key(self, db: AsyncSession, key_id: str):
        key = await api_key_repo.get(db, id=key_id)
        if key:
            await api_key_repo.update(db, db_obj=key, obj_in={"is_active": False})


class SecurityMonitoringService:
    async def generate_alert(self, db: AsyncSession, workspace_id: str, alert_type: str, severity: AlertSeverity, message: str, metadata: dict = None):
        alert_in = SecurityAlertInternalCreate(
            workspace_id=workspace_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            metadata_=metadata
        )
        return await security_alert_repo.create(db, obj_in=alert_in)
        
    async def get_alerts(self, db: AsyncSession, workspace_id: str) -> List[Any]:
        return await security_alert_repo.get_by_workspace(db, workspace_id)


class ComplianceService:
    async def export_user_data(self, db: AsyncSession, user_id: str, workspace_id: str) -> Dict[str, Any]:
        """GDPR Right to Access"""
        user = await user_repo.get(db, id=user_id)
        tickets = await ticket_repo.get_by_workspace(db, workspace_id) # Mock filtering by user
        
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat()
            },
            "tickets": [{"id": str(t.id), "title": t.title} for t in tickets],
            "exported_at": datetime.utcnow().isoformat()
        }
        
    async def delete_user_data(self, db: AsyncSession, user_id: str):
        """GDPR Right to Erasure - Hard delete or anonymize"""
        user = await user_repo.get(db, id=user_id)
        if user:
            # We use soft delete / anonymization to avoid cascading relational destruction
            await user_repo.update(db, db_obj=user, obj_in={
                "email": f"deleted_{user.id}@anonymized.com",
                "full_name": "Deleted User",
                "is_active": False
            })
            
            # Revoke all sessions
            sessions = await user_session_repo.get_active_by_user(db, user_id)
            for s in sessions:
                await user_session_repo.update(db, db_obj=s, obj_in={"is_revoked": True})


api_key_service = ApiKeyService()
security_monitoring = SecurityMonitoringService()
compliance_service = ComplianceService()
