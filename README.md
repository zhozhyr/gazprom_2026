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
  HTTP API, CRUD для справочников, lifecycle endpoints для permit, чтение notifications.
- `compliance_worker`
  Проверяет permit после `submit`.
  Если permit невалиден, переводит его в `rejected` и публикует `permits.compliance_failed`.
  Если permit валиден, публикует `permits.compliance_passed`.
- `approval_worker`
  Слушает `permits.compliance_passed` и переводит permit в `under_review`.
- `notification_worker`
  Слушает lifecycle-события и сохраняет уведомления в таблицу `notifications`.

### Хранилища и транспорт

- `PostgreSQL` для всех основных таблиц
- `Kafka` для событий между сервисами
- `Zookeeper` для локального Kafka-стенда

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
docker-compose.yml
README.md
CONTRIBUTING.md
```

## Доменные сущности

Основные таблицы:

- `facilities`
- `employees`
- `work_types`
- `permits`
- `permit_approvals`
- `permit_status_history`
- `notifications`

### Статусы permit

- `draft`
- `submitted`
- `under_review`
- `approved`
- `rejected`
- `in_progress`
- `completed`
- `cancelled`

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
  локальный запуск
- `.env.example`
  пример конфигурации
- `.env.docker`
  настройки для `docker compose`

Примеры:

- [api_service/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/.env)
- [approval_worker/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/approval_worker/.env)
- [compliance_worker/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/compliance_worker/.env)
- [notification_worker/.env](/Users/zhozhyr/PycharmProjects/gazprom/services/notification_worker/.env)

## Миграции

Миграции есть только у `api_service`, потому что схема базы контролируется через него.

Применить миграции:

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/api_service
poetry run alembic upgrade head
```

Откатить последнюю миграцию:

```bash
poetry run alembic downgrade -1
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

## Postman

Коллекция лежит здесь:

- [permit-api-service.postman_collection.json](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/tools/postman/permit-api-service.postman_collection.json)

В ней есть сценарии:

- setup справочников
- happy path permit lifecycle
- draft patch/delete
- compliance failure
- notifications
