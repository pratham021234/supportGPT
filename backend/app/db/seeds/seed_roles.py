import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.rbac import Role

async def seed_roles(session: AsyncSession):
    roles = [
        Role(name="ADMIN", description="Administrator with full access", is_system_role=True),
        Role(name="SUPPORT_AGENT", description="Standard support agent", is_system_role=True),
        Role(name="VIEWER", description="Read-only access", is_system_role=True)
    ]
    
    session.add_all(roles)
    await session.commit()
    print("Roles seeded successfully.")
