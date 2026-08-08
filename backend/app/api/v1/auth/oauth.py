from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets

from app.core.config import settings
from app.services.oauth_service import oauth
from app.dependencies.db import get_db
from app.repositories import user_repo, refresh_token_repo
from app.services.user_service import user_service
from app.schemas.user import UserCreate
from app.core.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth/google", tags=["oauth"])

@router.get("/login")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID:
        return {"success": False, "message": "Google OAuth is not configured."}
    redirect_uri = f"{settings.BACKEND_URL}/api/v1/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            user_info = await oauth.google.userinfo(token=token)
    except Exception as e:
        return {"success": False, "message": f"OAuth Error: {str(e)}"}

    email = user_info.get("email")
    full_name = user_info.get("name")
    avatar_url = user_info.get("picture")

    user = await user_repo.get_by_email(db, email=email)
    
    if not user:
        # Create user if it doesn't exist
        user_in = UserCreate(
            email=email,
            full_name=full_name,
            password=secrets.token_urlsafe(32) # Random secure password
        )
        user = await user_repo.create(db, obj_in=user_in)
        
        # Link avatar and provider
        await user_repo.update(db, db_obj=user, obj_in={
            "avatar_url": avatar_url,
            "provider": "google",
            "is_verified": True # Google verifies emails
        })
        
        await user_service.assign_role(db, str(user.id), "OWNER")
        user = await user_repo.get_with_roles(db, id=str(user.id))

    if not user.is_active:
        return {"success": False, "message": "Account disabled"}

    # Generate tokens
    roles = [r.role.name for r in user.roles]
    workspace_id = str(user.active_workspace_id) if user.active_workspace_id else None
    
    access_token = create_access_token(
        subject=str(user.id),
        email=user.email,
        workspace_id=workspace_id,
        roles=roles
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    
    expires_at = datetime.utcnow() + timedelta(days=7)
    await refresh_token_repo.create(db, obj_in={
        "user_id": str(user.id),
        "token_hash": refresh_token,
        "expires_at": expires_at.isoformat()
    })
    
    await user_repo.update(db, db_obj=user, obj_in={"last_login": datetime.utcnow().isoformat()})

    # Redirect to frontend with tokens (in practice, use HttpOnly cookies or query params securely)
    frontend_redirect_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(url=frontend_redirect_url)
