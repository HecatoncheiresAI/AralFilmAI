"""
Auth Service: регистрация, вход, обновление токена.

Соответствует Identity Service из главы 10.4 спецификации.
Бизнес-логика вынесена из роутера (app/api/v1/auth.py), чтобы
роутер оставался тонким, а логику можно было переиспользовать
(например, из будущего gRPC-интерфейса между сервисами).
"""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import TokenPair, UserCreate


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: UserCreate) -> User:
        existing = await self.db.execute(
            select(User).where((User.email == data.email) | (User.username == data.username))
        )
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email или username уже существует",
            )

        user = User(
            email=data.email,
            username=data.username,
            password_hash=hash_password(data.password),
            display_name=data.display_name,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )
        return user

    @staticmethod
    def issue_tokens(user_id: uuid.UUID) -> TokenPair:
        return TokenPair(
            access_token=create_token(user_id, "access"),
            refresh_token=create_token(user_id, "refresh"),
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("wrong token type")
            user_id = uuid.UUID(payload["sub"])
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный refresh-токен"
            )

        result = await self.db.execute(select(User).where(User.id == user_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

        return self.issue_tokens(user_id)
