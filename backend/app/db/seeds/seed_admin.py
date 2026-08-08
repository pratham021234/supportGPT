import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def seed_admin(session: AsyncSession):
    admin = User(
        email="admin@supportgpt.ai",
        full_name="System Administrator",
        provider="local",
        is_verified=True,
        is_active=True
    )
    
    session.add(admin)
    await session.commit()
    print("Admin user seeded successfully.")
