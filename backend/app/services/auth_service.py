import uuid
import secrets
from datetime import datetime, timedelta
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import user_repo, refresh_token_repo, email_verification_repo, password_reset_repo
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import BadRequestException, UnauthorizedException, NotFoundException
from app.services.email_service import email_service
from app.services.user_service import user_service
from app.services.audit_service import audit_service
from app.services.session_service import session_service
from app.models.user import User
from app.models.auth import RefreshToken

class AuthService:
    async def register(self, db: AsyncSession, data: RegisterRequest) -> User:
        existing_user = await user_repo.get_by_email(db, email=data.email)
        if existing_user:
            raise BadRequestException("Email already registered")

        hashed_password = get_password_hash(data.password)
        
        user_in = UserCreate(
            email=data.email,
            full_name=data.full_name,
            password=hashed_password
        )
        
        user = await user_repo.create(db, obj_in=user_in)
        
        # Assign OWNER role for new registration (or default to SUPPORT_AGENT based on business logic)
        # We'll use OWNER for simplicity in this SaaS architecture
        await user_service.assign_role(db, str(user.id), "OWNER")
        
        # Create verification token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        await email_verification_repo.create(db, obj_in={
            "user_id": str(user.id),
            "token": token,
            "expires_at": expires_at.isoformat()
        })
        
        await email_service.send_verification_email(user.email, token)
        
        await audit_service.log_action(db, str(user.id), "User Registered", "user", str(user.id))
        
        return await user_repo.get_with_roles(db, id=str(user.id))

    async def verify_email(self, db: AsyncSession, token: str) -> bool:
        verification = await email_verification_repo.get_by_token(db, token=token)
        if not verification:
            raise BadRequestException("Invalid or expired token")
        
        if verification.used:
            raise BadRequestException("Token already used")
            
        if verification.expires_at.replace(tzinfo=None) < datetime.utcnow():
            raise BadRequestException("Token expired")
            
        # Mark as used and verify user
        await email_verification_repo.update(db, db_obj=verification, obj_in={"used": True})
        
        user = await user_repo.get(db, id=verification.user_id)
        if user:
            await user_repo.update(db, db_obj=user, obj_in={"is_verified": True})
            return True
        return False

    async def login(self, db: AsyncSession, data: LoginRequest, ip_address: str = None, user_agent: str = None) -> Tuple[str, str, User]:
        user = await user_repo.get_by_email(db, email=data.email)
        if not user or not user.password_hash:
            raise UnauthorizedException("Incorrect email or password")
            
        if not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Incorrect email or password")
            
        if not user.is_active:
            raise UnauthorizedException("Inactive user")
            
        if not user.is_verified:
            raise UnauthorizedException("Email not verified")

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
        
        # Store refresh token (using the plain token as hash for simplicity, or hash it in prod)
        await refresh_token_repo.create(db, obj_in={
            "user_id": str(user.id),
            "token_hash": refresh_token,
            "expires_at": expires_at.isoformat()
        })
        
        # Update last login
        await user_repo.update(db, db_obj=user, obj_in={"last_login": datetime.utcnow().isoformat()})
        
        # Create user session
        await session_service.create_session(
            db=db,
            user_id=str(user.id),
            refresh_token=refresh_token,
            expires_at=expires_at.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Log login
        await audit_service.log_action(db, str(user.id), "User Logged In", "user", str(user.id), metadata_={"ip": ip_address})
        
        return access_token, refresh_token, user

    async def refresh(self, db: AsyncSession, refresh_token: str, ip_address: str = None, user_agent: str = None) -> Tuple[str, str]:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
            
        user_id = payload.get("sub")
        
        db_token = await refresh_token_repo.get_by_token_hash(db, token_hash=refresh_token)
        if not db_token:
            raise UnauthorizedException("Refresh token not found")
            
        if db_token.is_revoked:
            raise UnauthorizedException("Refresh token revoked")
            
        if db_token.expires_at.replace(tzinfo=None) < datetime.utcnow():
            raise UnauthorizedException("Refresh token expired")
            
        user = await user_repo.get_with_roles(db, id=user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
            
        # Rotate token
        await refresh_token_repo.update(db, db_obj=db_token, obj_in={"is_revoked": True})
        
        roles = [r.role.name for r in user.roles]
        workspace_id = str(user.active_workspace_id) if user.active_workspace_id else None
        
        new_access_token = create_access_token(
            subject=str(user.id), 
            email=user.email,
            workspace_id=workspace_id,
            roles=roles
        )
        new_refresh_token = create_refresh_token(subject=str(user.id))
        
        expires_at = datetime.utcnow() + timedelta(days=7)
        await refresh_token_repo.create(db, obj_in={
            "user_id": str(user.id),
            "token_hash": new_refresh_token,
            "expires_at": expires_at.isoformat()
        })
        
        # Update session
        await session_service.revoke_session(db, refresh_token)
        await session_service.create_session(
            db=db,
            user_id=str(user.id),
            refresh_token=new_refresh_token,
            expires_at=expires_at.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        await audit_service.log_action(db, str(user.id), "Token Refreshed", "user", str(user.id), metadata_={"ip": ip_address})
        
        return new_access_token, new_refresh_token

    async def logout(self, db: AsyncSession, refresh_token: str) -> bool:
        db_token = await refresh_token_repo.get_by_token_hash(db, token_hash=refresh_token)
        if db_token:
            await refresh_token_repo.update(db, db_obj=db_token, obj_in={"is_revoked": True})
            await session_service.revoke_session(db, refresh_token)
            await audit_service.log_action(db, str(db_token.user_id), "User Logged Out", "user", str(db_token.user_id))
        return True

    async def logout_all(self, db: AsyncSession, user_id: str) -> bool:
        await session_service.revoke_all_sessions(db, user_id)
        # also revoke all refresh tokens manually via repo if needed, but session service acts as primary now.
        tokens = await refresh_token_repo.get_multi(db)
        for t in tokens:
            if str(t.user_id) == user_id and not t.is_revoked:
                await refresh_token_repo.update(db, db_obj=t, obj_in={"is_revoked": True})
        
        await audit_service.log_action(db, user_id, "User Logged Out All Sessions", "user", user_id)
        return True

    async def forgot_password(self, db: AsyncSession, email: str) -> bool:
        user = await user_repo.get_by_email(db, email=email)
        if not user:
            # Return true to prevent email enumeration
            return True
            
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        await password_reset_repo.create(db, obj_in={
            "user_id": str(user.id),
            "token": token,
            "expires_at": expires_at.isoformat()
        })
        
        await email_service.send_password_reset_email(user.email, token)
        await audit_service.log_action(db, str(user.id), "Password Reset Requested", "user", str(user.id))
        return True

    async def reset_password(self, db: AsyncSession, token: str, new_password: str) -> bool:
        reset_record = await password_reset_repo.get_by_token(db, token=token)
        if not reset_record:
            raise BadRequestException("Invalid or expired token")
            
        if reset_record.used:
            raise BadRequestException("Token already used")
            
        if reset_record.expires_at.replace(tzinfo=None) < datetime.utcnow():
            raise BadRequestException("Token expired")
            
        user = await user_repo.get(db, id=reset_record.user_id)
        if not user:
            raise BadRequestException("User not found")
            
        hashed_password = get_password_hash(new_password)
        await user_repo.update(db, db_obj=user, obj_in={"password_hash": hashed_password})
        
        await password_reset_repo.update(db, db_obj=reset_record, obj_in={"used": True})
        
        # Invalidate all refresh tokens and sessions
        for rt in user.refresh_tokens:
            if not rt.is_revoked:
                await refresh_token_repo.update(db, db_obj=rt, obj_in={"is_revoked": True})
        await session_service.revoke_all_sessions(db, str(user.id))
                
        await audit_service.log_action(db, str(user.id), "Password Reset Completed", "user", str(user.id))
        return True

auth_service = AuthService()
