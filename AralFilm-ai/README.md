# AralFilm AI Platform

Реализация по AI Master Specification (AMS). Разработка ведётся по фазам
(глава 21 спецификации):

- [x] **Phase 0 / начало Phase 1 — Foundation**: структура репозитория,
      `User`/`Organization`/`Membership`/`Project`, JWT-аутентификация,
      Project CRUD API, Alembic-миграции, Docker Compose (Postgres, Redis,
      MinIO, RabbitMQ).
- [ ] **Phase 1 (продолжение) — AI Core**: Prompt Engine, AI Provider
      Layer (адаптеры), Director/Screenwriter/Character-агенты,
      Workflow Engine, Creative Graph Service.
- [ ] **Phase 1 (продолжение) — Media**: генерация изображений/видео,
      Asset Service, базовый Render Engine.
- [ ] **Phase 2+ — Studio / Enterprise**: команды, биллинг, marketplace.

## Быстрый старт (backend)

```bash
cd backend
cp .env.example .env        # заполнить SECRET_KEY и т.д.
pip install -r requirements.txt

# поднять инфраструктуру (Postgres, Redis, MinIO, RabbitMQ)
docker compose -f ../infrastructure/docker-compose.yml up -d postgres redis minio rabbitmq

# применить миграции
alembic upgrade head

# запустить API
uvicorn app.main:app --reload
```

Документация API: `http://localhost:8000/docs`

## Структура

```
AralFilm-ai/
├── backend/
│   ├── app/
│   │   ├── core/        # config, security (JWT/bcrypt)
│   │   ├── db/           # SQLAlchemy Base, сессия
│   │   ├── models/       # ORM: User, Organization, Project, ...
│   │   ├── schemas/      # Pydantic DTO
│   │   ├── services/     # бизнес-логика (Auth Service, Project Service)
│   │   └── api/v1/       # FastAPI роутеры
│   ├── migrations/       # Alembic
│   └── tests/
└── infrastructure/
    └── docker-compose.yml
```

## Реализованные API (Часть 1)

| Метод | Путь | Описание |
|---|---|---|
| POST | `/api/v1/auth/register` | Регистрация пользователя |
| POST | `/api/v1/auth/login` | Вход, получение access/refresh токенов |
| POST | `/api/v1/auth/refresh` | Обновление access-токена |
| GET  | `/api/v1/auth/me` | Текущий пользователь |
| POST | `/api/v1/projects` | Создать проект |
| GET  | `/api/v1/projects` | Список проектов пользователя |
| GET  | `/api/v1/projects/{id}` | Получить проект |
| PUT  | `/api/v1/projects/{id}` | Обновить проект |
| DELETE | `/api/v1/projects/{id}` | Удалить проект |
