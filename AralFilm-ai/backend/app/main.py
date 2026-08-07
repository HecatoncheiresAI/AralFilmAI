"""
Точка входа backend-приложения AralFilm AI.

На этапе MVP (Phase 1, глава 21.3) backend/project-service/auth-service
объединены в один процесс FastAPI для скорости разработки. Дробление
на отдельные микросервисы (services/identity, services/project, ...
из главы 22.7) выполняется позже, когда появится нагрузка,
требующая независимого масштабирования — сама структура кода
(роутеры/сервисы/модели по доменам) уже готова к этому разделению.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="AI Master Specification (AMS) — Phase 1: MVP Creator Platform",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.PROJECT_NAME}
