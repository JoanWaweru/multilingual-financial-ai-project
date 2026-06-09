"""
Authentication service for user registration and JWT auth.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
import hashlib
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, expires_minutes: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.auth_secret_key, algorithm=settings.auth_algorithm)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not creds or not creds.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.auth_secret_key,
            algorithms=[settings.auth_algorithm]
        )
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_current_user_optional(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not creds or not creds.credentials:
        return None
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.auth_secret_key,
            algorithms=[settings.auth_algorithm]
        )
        user_id = payload.get("sub")
    except JWTError:
        return None
    if not user_id:
        return None
    return await get_user_by_id(db, user_id)


def require_roles(roles: list[str]):
    async def _dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _dependency


async def create_user(db: AsyncSession, email: str, password: str, full_name: Optional[str] = None) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        session_id=str(uuid4()),
        role="user"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_password_reset(db: AsyncSession, user: User) -> str:
    token = secrets.token_urlsafe(24)
    user.reset_token_hash = _hash_reset_token(token)
    user.reset_token_expires = datetime.utcnow() + timedelta(
        minutes=settings.password_reset_token_ttl_minutes
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return token


async def reset_password_with_token(db: AsyncSession, token: str, new_password: str) -> bool:
    token_hash = _hash_reset_token(token)
    result = await db.execute(select(User).where(User.reset_token_hash == token_hash))
    user = result.scalar_one_or_none()
    if not user:
        return False
    if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        return False
    user.password_hash = hash_password(new_password)
    user.reset_token_hash = None
    user.reset_token_expires = None
    db.add(user)
    await db.commit()
    return True
