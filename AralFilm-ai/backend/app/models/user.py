"""
Identity-модели: User, Organization, Membership.

Соответствует главе 3.2 (Пользователь) и главе 10.4 (Identity Service).
Модель доступа по спецификации:
    User -> Organization -> Team -> Role -> Permission
Роли (глава 10.4): OWNER, ADMIN, DIRECTOR, EDITOR, WRITER, VIEWER
"""
import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDMixin


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class OrgRole(str, enum.Enum):
    """Роли из главы 10.4 Identity Service."""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    DIRECTOR = "DIRECTOR"
    EDITOR = "EDITOR"
    WRITER = "WRITER"
    VIEWER = "VIEWER"


class SubscriptionPlan(str, enum.Enum):
    """Тарифы из главы 18.12."""
    FREE = "FREE"
    CREATOR = "CREATOR"
    STUDIO = "STUDIO"
    ENTERPRISE = "ENTERPRISE"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="ru")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Organization(UUIDMixin, TimestampMixin, Base):
    """Поддержка студий и команд (глава 10.6, 18.4)."""
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class Membership(UUIDMixin, TimestampMixin, Base):
    """Связь пользователей и организаций (глава 11.7)."""
    __tablename__ = "memberships"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    role: Mapped[OrgRole] = mapped_column(Enum(OrgRole), default=OrgRole.VIEWER, nullable=False)

    user: Mapped["User"] = relationship(back_populates="memberships")
    organization: Mapped["Organization"] = relationship(back_populates="memberships")
