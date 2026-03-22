# API Service

MVP-сервис для платформы управления нарядами-допусками.

## Что есть сейчас

- `FastAPI` приложение
- `SQLAlchemy` async модели и сессии
- базовые справочники:
  - `facilities`
  - `employees`
  - `work_types`
- workflow по `permits`
- publish событий в Kafka при `submit` и `approve/reject`
- базовый unit test для сценария создания и согласования наряда

## Запуск

```bash
cd services/api_service
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --app-dir src --reload
```

Локальные настройки берутся из [`.env`](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/.env).
Docker-сценарий использует отдельный файл [`.env.docker`](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/.env.docker) с `Postgres` и `Kafka`.

## Миграции

Применить миграции:

```bash
poetry run alembic upgrade head
```

Если локальная `sqlite`-база была создана старым `create_all`, сначала либо удалите файл БД и примените миграции заново:

```bash
rm -f permit_api.db
poetry run alembic upgrade head
```

либо пометьте текущую схему как уже соответствующую первой ревизии:

```bash
poetry run alembic stamp head
```

Откатить последнюю миграцию:

```bash
poetry run alembic downgrade -1
```

## Базовые endpoints

- `GET /health`
- `POST /facilities`
- `GET /facilities`
- `POST /employees`
- `GET /employees`
- `POST /work-types`
- `GET /work-types`
- `POST /permits`
- `GET /permits`
- `GET /permits/{id}`
- `POST /permits/{id}/submit`
- `POST /permits/{id}/approve`
- `POST /permits/{id}/reject`
