from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Dict, Any
from app.dependencies import get_db, get_current_active_user, require_owner
from app.services import auth_service
from app.schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
    ResendVerificationRequest,
    UserResponse,
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Dict[str, Any])
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await auth_service.register(db, request)

    return {
        "success": True,
        "message": "Registration successful. Please check your email to verify your account.",
        "data": UserResponse.model_validate(user).model_dump()
    }


@router.post("/login", response_model=Dict[str, Any])
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    access_token, refresh_token, user = await auth_service.login(
        db,
        login_data,
        ip_address,
        user_agent
    )

    auth_response = AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

    return {
        "success": True,
        "message": "Login successful",
        "data": auth_response.model_dump()
    }


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    access_token, refresh_token = await auth_service.refresh(
        db,
        refresh_data.refresh_token,
        ip_address,
        user_agent
    )

    return {
        "success": True,
        "message": "Token refreshed",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    await auth_service.logout(db, request.refresh_token)

    return {
        "success": True,
        "message": "Successfully logged out"
    }


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await auth_service.logout_all(db, str(current_user.id))

    return {
        "success": True,
        "message": "Successfully logged out of all sessions"
    }


@router.get("/me", response_model=Dict[str, Any])
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    return {
        "success": True,
        "message": "User fetched successfully",
        "data": UserResponse.model_validate(current_user).model_dump()
    }


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    await auth_service.verify_email(db, token)

    return {
        "success": True,
        "message": "Email verified successfully"
    }


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    await auth_service.forgot_password(db, request.email)

    return {
        "success": True,
        "message": "If that email is registered, a password reset link has been sent."
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    await auth_service.reset_password(
        db,
        request.token,
        request.new_password
    )

    return {
        "success": True,
        "message": "Password has been successfully reset."
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await auth_service.change_password(
        db,
        str(current_user.id),
        request.current_password,
        request.new_password
    )

    return {
        "success": True,
        "message": "Password changed successfully"
    }


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    await auth_service.resend_verification(db, request.email)

    return {
        "success": True,
        "message": "Verification email resent if account exists and is not verified"
    }


@router.get("/admin/analytics", dependencies=[Depends(require_owner)])
async def get_admin_analytics(
    current_user: User = Depends(get_current_active_user)
):
    return {
        "success": True,
        "message": "Admin access granted",
        "data": {
            "metrics": "secret"
        }
    }