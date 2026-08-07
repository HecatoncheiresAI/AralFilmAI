"""
Общие миксины для ORM-моделей.

Согласно главе 3.1 спецификации ("Общая концепция"):
    Все объекты имеют:
        - UUID
        - владельца
        - дату создания и изменения
        - версию
        - статус
        - историю изменений
        - ссылки на связанные сущности
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class VersionMixin:
    """Оптимистичная блокировка + история версий (глава 3.17: Version)."""
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
