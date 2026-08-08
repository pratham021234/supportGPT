from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.rbac import Permission, Role, RolePermission
from app.repositories import permission_repo, role_repo, role_permission_repo
from app.repositories.rbac_repo import RoleInternalCreate, RolePermissionCreate
import uuid

# Base Permissions according to Prompt
BASE_PERMISSIONS = [
    {"name": "manage_team", "resource": "team", "action": "manage", "description": "Can manage workspace team members"},
    {"name": "manage_workspace", "resource": "workspace", "action": "manage", "description": "Can manage workspace settings"},
    {"name": "manage_agents", "resource": "agents", "action": "manage", "description": "Can manage AI agents"},
    {"name": "manage_documents", "resource": "documents", "action": "manage", "description": "Can manage knowledge base documents"},
    {"name": "manage_conversations", "resource": "conversations", "action": "manage", "description": "Can manage all conversations"},
    {"name": "manage_tickets", "resource": "tickets", "action": "manage", "description": "Can manage support tickets"},
    {"name": "manage_analytics", "resource": "analytics", "action": "manage", "description": "Can view and manage analytics"},
    {"name": "manage_billing", "resource": "billing", "action": "manage", "description": "Can manage subscription and billing"},
    {"name": "knowledge:read", "resource": "knowledge", "action": "read", "description": "View knowledge base documents and FAQs"},
    {"name": "knowledge:create", "resource": "knowledge", "action": "create", "description": "Upload documents and create FAQs"},
    {"name": "knowledge:manage", "resource": "knowledge", "action": "manage", "description": "Edit, archive, and organize knowledge"},
    {"name": "knowledge:delete", "resource": "knowledge", "action": "delete", "description": "Permanently delete knowledge sources and documents"},
    {"name": "view_documents", "resource": "documents", "action": "view", "description": "Can view documents"},
    {"name": "view_analytics", "resource": "analytics", "action": "view", "description": "Can view analytics"},
    {"name": "create_agent", "resource": "agents", "action": "create", "description": "Can create AI agents"},
    {"name": "delete_agent", "resource": "agents", "action": "delete", "description": "Can delete AI agents"},
    {"name": "assign_ticket", "resource": "tickets", "action": "assign", "description": "Can assign support tickets"},
    {"name": "respond_conversation", "resource": "conversations", "action": "respond", "description": "Can respond to customer conversations"}
]

# System Roles and their permissions mapping
SYSTEM_ROLES = {
    "OWNER": ["manage_team", "manage_workspace", "manage_agents", "manage_documents", "manage_conversations", "manage_tickets", "manage_analytics", "manage_billing", "view_documents", "view_analytics", "create_agent", "delete_agent", "assign_ticket", "respond_conversation", "knowledge:read", "knowledge:create", "knowledge:manage", "knowledge:delete"],
    "ADMIN": ["manage_team", "manage_agents", "manage_documents", "manage_conversations", "manage_tickets", "manage_analytics", "view_documents", "view_analytics", "create_agent", "assign_ticket", "respond_conversation", "knowledge:read", "knowledge:create", "knowledge:manage", "knowledge:delete"],
    "SUPPORT_MANAGER": ["manage_conversations", "assign_ticket", "view_analytics", "manage_team", "knowledge:read", "knowledge:create", "knowledge:manage"],
    "SUPPORT_AGENT": ["respond_conversation", "assign_ticket", "view_documents", "knowledge:read", "knowledge:create"],
    "VIEWER": ["view_documents", "view_analytics", "knowledge:read"]
}

async def init_db(db: AsyncSession):
    # 1. Create permissions if they don't exist
    db_perms = await permission_repo.get_all(db)
    perm_map = {p.name: p for p in db_perms}
    
    for perm_data in BASE_PERMISSIONS:
        if perm_data["name"] not in perm_map:
            perm = Permission(**perm_data)
            db.add(perm)
            perm_map[perm_data["name"]] = perm
            
    await db.commit()

    # 2. Create System Roles
    for role_name, perms in SYSTEM_ROLES.items():
        role = await role_repo.get_by_name_and_workspace(db, name=role_name, workspace_id=None)
        if not role:
            role_in = RoleInternalCreate(name=role_name, is_system_role=True, description=f"System role: {role_name}")
            role = await role_repo.create(db, obj_in=role_in)
            
        # 3. Assign Permissions to Role
        existing_rp = await role_permission_repo.get_by_role(db, str(role.id))
        existing_perm_ids = {str(rp.permission_id) for rp in existing_rp}
        
        for perm_name in perms:
            perm = perm_map.get(perm_name)
            if perm and str(perm.id) not in existing_perm_ids:
                rp_in = RolePermissionCreate(role_id=str(role.id), permission_id=str(perm.id))
                await role_permission_repo.create(db, obj_in=rp_in)
                existing_perm_ids.add(str(perm.id))
