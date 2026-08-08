import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.workspace import Workspace
from app.models.user import User

async def seed_workspace(session: AsyncSession):
    # Fetch admin to set as owner
    result = await session.execute(select(User).filter_by(email="admin@supportgpt.ai"))
    admin = result.scalar_one_or_none()
    
    if not admin:
        print("Run seed_admin first.")
        return

    workspace = Workspace(
        name="SupportGPT HQ",
        slug="supportgpt-hq",
        description="Main workspace for SupportGPT",
        industry="Technology",
        plan="enterprise",
        owner_id=admin.id
    )
    
    session.add(workspace)
    await session.commit()
    print("Workspace seeded successfully.")
