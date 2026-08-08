import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rbac import Permission

async def seed_permissions(session: AsyncSession):
    permissions = [
        Permission(name="MANAGE_WORKSPACES", resource="workspace", action="manage", description="Manage workspace settings"),
        Permission(name="MANAGE_AGENTS", resource="agent", action="manage", description="Create and modify AI agents"),
        Permission(name="VIEW_CONVERSATIONS", resource="conversation", action="view", description="View customer conversations"),
        Permission(name="MANAGE_KNOWLEDGE", resource="knowledge", action="manage", description="Upload and manage knowledge sources")
    ]
    
    session.add_all(permissions)
    await session.commit()
    print("Permissions seeded successfully.")
