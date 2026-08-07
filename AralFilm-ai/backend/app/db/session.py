"""
Слой подключения к главной транзакционной базе данных (глава 11.3:
PostgreSQL Core Database). Используется асинхронный SQLAlchemy,
т.к. вся платформа строится на асинхронной обработке (глава 6:
Нефункциональные требования — асинхронная обработка длительных задач).
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей платформы."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI-зависимость: сессия БД на время запроса."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
