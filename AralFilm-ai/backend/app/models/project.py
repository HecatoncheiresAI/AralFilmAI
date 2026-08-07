"""
Project — главная сущность системы (глава 3.3, 11.8).

Дерево объектов проекта (глава 3.1):
    Organization -> User -> Project -> {Concept, Script, Storyboard,
    Character Library, Environment Library, Style Library, Scene[],
    Asset Library, Workflow, Export}

В этой части реализована базовая сущность Project и её настройки
(project_settings, глава 11.9). Concept/Script/Scene/Character и т.д.
будут добавлены в Части 2 (AI Core) при реализации Workflow Engine.
"""
import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.base import TimestampMixin, UUIDMixin, VersionMixin


class ProjectType(str, enum.Enum):
    """Типы проектов (глава 3.3 / 11.8)."""
    MOVIE = "MOVIE"
    SHORT_FILM = "SHORT_FILM"
    COMMERCIAL = "COMMERCIAL"
    MUSIC_VIDEO = "MUSIC_VIDEO"
    ANIMATION = "ANIMATION"
    DOCUMENTARY = "DOCUMENTARY"
    TRAILER = "TRAILER"
    PRESENTATION = "PRESENTATION"
    TRAINING = "TRAINING"
    SOCIAL_CONTENT = "SOCIAL_CONTENT"


class ProjectStatus(str, enum.Enum):
    """Статусы проекта (глава 3.3) и жизненный цикл (глава 7.3)."""
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    GENERATING = "GENERATING"
    EDITING = "EDITING"
    RENDERING = "RENDERING"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class Project(UUIDMixin, TimestampMixin, VersionMixin, Base):
    __tablename__ = "projects"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[ProjectType] = mapped_column(Enum(ProjectType), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False
    )

    resolution: Mapped[str] = mapped_column(String(16), default="1080p")
    fps: Mapped[int] = mapped_column(Integer, default=24)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    aspect_ratio: Mapped[str] = mapped_column(String(16), default="16:9")
    language: Mapped[str] = mapped_column(String(8), default="ru")
    target_platform: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # style_profile хранится как JSON-ссылка/встроенный профиль (глава 3.10)
    style_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    settings: Mapped["ProjectSettings | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )


class ProjectSettings(UUIDMixin, Base):
    """project_settings (глава 11.9)."""
    __tablename__ = "project_settings"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), unique=True
    )
    quality_level: Mapped[str] = mapped_column(String(32), default="standard")
    budget_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    default_models: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="settings")
