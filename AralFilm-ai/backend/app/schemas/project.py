import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectStatus, ProjectType


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    type: ProjectType
    organization_id: uuid.UUID | None = None
    resolution: str = "1080p"
    fps: int = Field(default=24, ge=1, le=120)
    aspect_ratio: str = "16:9"
    language: str = "ru"


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus | None = None
    resolution: str | None = None
    fps: int | None = Field(default=None, ge=1, le=120)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    organization_id: uuid.UUID | None
    title: str
    description: str | None
    type: ProjectType
    status: ProjectStatus
    resolution: str
    fps: int
    duration: float | None
    aspect_ratio: str
    language: str
    version: int
    created_at: datetime
    updated_at: datetime
