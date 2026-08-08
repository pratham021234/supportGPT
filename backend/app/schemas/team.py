from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

# --- Permissions ---
class PermissionResponse(BaseModel):
    id: UUID
    name: str
    resource: str
    action: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

# --- Roles ---
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: List[UUID]

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[UUID]] = None

class RoleResponse(RoleBase):
    id: UUID
    workspace_id: Optional[UUID] = None
    is_system_role: bool
    created_at: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True

# --- Team Members ---
class MemberRoleResponse(BaseModel):
    id: UUID
    role: RoleResponse

    class Config:
        from_attributes = True

class TeamMemberResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    user_id: UUID
    status: str
    joined_at: datetime
    
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None
    roles: List[MemberRoleResponse] = []

    class Config:
        from_attributes = True

class AssignRoleRequest(BaseModel):
    role_id: UUID

class UpdateMemberStatusRequest(BaseModel):
    status: str

# --- Transfer Ownership ---
class TransferOwnershipRequest(BaseModel):
    new_owner_member_id: UUID
