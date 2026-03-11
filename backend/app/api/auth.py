"""
Authentication API routes
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.auth_service import (
    create_access_token,
    create_user,
    create_password_reset,
    get_current_user,
    get_user_by_email,
    reset_password_with_token,
    verify_password
)

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, request.email, request.password, request.full_name)
    token = create_access_token(user.id, settings.auth_access_token_minutes)
    return AuthResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, request.email)
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, settings.auth_access_token_minutes)
    return AuthResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, request.email)
    reset_token = None
    if user and user.password_hash:
        reset_token = await create_password_reset(db, user)
    return ForgotPasswordResponse(
        message="If the email exists, a reset token has been generated.",
        reset_token=reset_token
    )


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    ok = await reset_password_with_token(db, request.token, request.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    return {"message": "Password reset successful"}
