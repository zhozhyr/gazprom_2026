# Gazprom Permit Platform

Monorepo для MVP платформы управления нарядами-допусками на объектах газовой инфраструктуры.

Проект построен как event-driven backend на `FastAPI`, `PostgreSQL`, `Kafka`, `SQLAlchemy`, `Alembic` и `Poetry`.

## Что умеет система

- вести справочники объектов, сотрудников и типов работ
- создавать наряды-допуски
- редактировать и удалять наряды в статусе `draft`
- отправлять наряд в workflow через `submit`
- автоматически проверять permit на минимальные compliance-условия
- автоматически переводить валидный permit в `under_review`
- автоматически формировать уведомления по событиям
- хранить историю статусов permit

## Архитектура

Текущий pipeline:

```text
api_service -> Kafka(topic permits.submitted) -> compliance_worker
compliance_worker -> Kafka(topic permits.compliance_passed / permits.compliance_failed)
permits.compliance_passed -> approval_worker
permits.submitted / permits.compliance_* -> notification_worker
```

### Сервисы

- `api_service`
  HTTP API, справочники, permit lifecycle, чтение notifications, миграции.
- `compliance_worker`
  Проверяет permit после `submit`.
- `approval_worker`
  Слушает `permits.compliance_passed` и переводит permit в `under_review`.
- `notification_worker`
  Слушает lifecycle-события и сохраняет уведомления в таблицу `notifications`.

## Структура репозитория

```text
services/
  api_service/
    src/app/
    src/tests/
    migrations/
  approval_worker/
    src/app/
    src/tests/
  compliance_worker/
    src/app/
    src/tests/
  notification_worker/
    src/app/
    src/tests/
.github/workflows/
docker-compose.yml
README.md
CONTRIBUTING.md
```

## Основные таблицы

- `facilities`
- `employees`
- `work_types`
- `permits`
- `permit_approvals`
- `permit_status_history`
- `notifications`

## API

### Health

- `GET /health`

### Facilities

- `POST /facilities`
- `GET /facilities`

### Employees

- `POST /employees`
- `GET /employees`

### Work Types

- `POST /work-types`
- `GET /work-types`

### Permits

- `POST /permits`
- `GET /permits`
- `GET /permits/{id}`
- `PATCH /permits/{id}`
- `DELETE /permits/{id}`
- `POST /permits/{id}/submit`
- `POST /permits/{id}/approve`
- `POST /permits/{id}/reject`

### Notifications

- `GET /notifications`
- `GET /notifications/{id}`

## Быстрый старт

### Весь стек через Docker

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom
docker compose up -d --build
```

Swagger:

- [http://localhost:8000/docs](http://localhost:8000/docs)

### Локальный запуск только `api_service`

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/api_service
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --app-dir src --reload
```

## Конфигурация

У каждого сервиса свой набор env-файлов:

- `.env`
- `.env.example`
- `.env.docker`

Примеры:

- [api_service/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/.env)
- [approval_worker/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/approval_worker/.env)
- [compliance_worker/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/compliance_worker/.env)
- [notification_worker/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/notification_worker/.env)

## Миграции

Миграции есть у `api_service`.

Применить миграции:

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/api_service
poetry run alembic upgrade head
```

## Тесты

### api_service

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/api_service
poetry run pytest -q
```

### approval_worker

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/approval_worker
poetry run pytest -q
```

### compliance_worker

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/compliance_worker
poetry run pytest -q
```

### notification_worker

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/notification_worker
poetry run pytest -q
```

## CI

В репозитории настроен GitHub Actions workflow:

- [ci.yml](/Users/zhozhyr/PycharmProjects/gazprom/.github/workflows/ci.yml)

Что делает workflow:

- job `test`
  запускает `pytest` для:
  - `api_service`
  - `approval_worker`
  - `compliance_worker`
  - `notification_worker`
- job `build`
  собирает Docker-образы всех сервисов после успешных тестов

## Postman

Коллекция лежит здесь:

- [permit-api-service.postman_collection.json](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/tools/postman/permit-api-service.postman_collection.json)

В ней есть сценарии:

- setup справочников
- happy path permit lifecycle
- draft patch/delete
- compliance failure
- notifications
