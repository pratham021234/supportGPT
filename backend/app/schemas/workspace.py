from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

# --- Workspace Schemas ---
class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None

class WorkspaceResponse(WorkspaceBase):
    id: UUID
    slug: str
    plan: str
    is_active: bool
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Workspace Member Schemas ---
class WorkspaceMemberBase(BaseModel):
    workspace_id: UUID
    user_id: UUID
    status: str = "ACTIVE"

class WorkspaceMemberCreate(WorkspaceMemberBase):
    pass

class WorkspaceMemberResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    status: str
    joined_at: datetime
    
    # We might want to include nested user data for the frontend
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None

    class Config:
        from_attributes = True

class WorkspaceMemberUpdate(BaseModel):
    role: str

# --- Workspace Invitation Schemas ---
class WorkspaceInvitationCreate(BaseModel):
    email: EmailStr
    role: str

class WorkspaceInvitationResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    email: EmailStr
    role: str
    expires_at: datetime
    accepted: bool
    invited_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AcceptInvitationRequest(BaseModel):
    token: str

# --- Workspace Audit Log Schemas ---
class WorkspaceAuditLogResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    actor_id: Optional[UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    metadata_: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True
