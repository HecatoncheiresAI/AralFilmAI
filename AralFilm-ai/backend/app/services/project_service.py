"""
Project Service: центральный бизнес-сервис платформы (глава 10.6).

Пока реализованы базовые операции CRUD над Project (глава 12.5-12.6:
POST /projects, GET /projects/{id}, PUT /projects/{id}, DELETE /projects/{id}).
Scene/Character/Storyboard будут добавлены в Части 2 при реализации
Workflow Engine и Creative Graph Service.
"""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, owner: User, data: ProjectCreate) -> Project:
        project = Project(
            owner_id=owner.id,
            organization_id=data.organization_id,
            title=data.title,
            description=data.description,
            type=data.type,
            resolution=data.resolution,
            fps=data.fps,
            aspect_ratio=data.aspect_ratio,
            language=data.language,
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_owned(self, owner: User, project_id: uuid.UUID) -> Project:
        """Возвращает проект, только если он принадлежит пользователю.

        Полноценная проверка прав (RBAC/ABAC по организации, роли Editor/
        Director и т.д. из главы 13.7) будет добавлена вместе с Identity
        Service после реализации Membership-based авторизации.
        """
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проект не найден")
        if project.owner_id != owner.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к проекту")
        return project

    async def list_owned(self, owner: User, limit: int = 50, offset: int = 0) -> list[Project]:
        result = await self.db.execute(
            select(Project)
            .where(Project.owner_id == owner.id)
            .order_by(Project.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update(self, owner: User, project_id: uuid.UUID, data: ProjectUpdate) -> Project:
        project = await self.get_owned(owner, project_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        project.version += 1
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, owner: User, project_id: uuid.UUID) -> None:
        project = await self.get_owned(owner, project_id)
        await self.db.delete(project)
        await self.db.commit()
