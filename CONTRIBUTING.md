# Contributing

## Общие правила

- Держим monorepo-структуру в формате `services/<service_name>/src/app` и `services/<service_name>/src/tests`.
- У каждого сервиса должны быть:
  - `pyproject.toml`
  - `poetry.toml`
  - `.env`
  - `.env.example`
  - `.env.docker`
  - `README.md`
- Для ручных правок файлов используем точечные изменения и не ломаем существующий pipeline.

## Новые сервисы

При добавлении нового микросервиса:

1. Создайте папку:

```text
services/<service_name>/
  src/app/
  src/tests/
```

2. Добавьте:

- `pyproject.toml`
- `poetry.toml`
- `Dockerfile`
- `README.md`
- `.env`, `.env.example`, `.env.docker`

3. Подключите сервис в [docker-compose.yml](/Users/zhozhyr/PycharmProjects/gazprom/docker-compose.yml).

4. Добавьте хотя бы базовые unit-тесты.

## Стиль архитектуры

- `api_service` отвечает за HTTP API, миграции и чтение/запись основных сущностей.
- Воркеры должны быть максимально узкими по ответственности.
- Общение между сервисами идет через Kafka topics.
- Один сервис не должен дублировать бизнес-логику другого без необходимости.

## База данных

- Схема БД контролируется через `Alembic` в `services/api_service`.
- Не использовать `create_all` как основной способ создания схемы в production-like сценариях.
- При изменении таблиц `api_service` нужно добавлять новую миграцию в:
  [migrations/versions](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/migrations/versions)

## Конфигурация

- Не хардкодить настройки в Python-коде.
- Все runtime-настройки должны идти через env.
- Для локального запуска использовать `.env`.
- Для `docker compose` использовать `.env.docker`.

## Тесты

Перед коммитом желательно прогонять тесты измененного сервиса.

Примеры:

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/api_service
poetry run pytest -q
```

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/compliance_worker
poetry run pytest -q
```

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/approval_worker
poetry run pytest -q
```

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom/services/notification_worker
poetry run pytest -q
```

## Docker

Если меняется код сервиса, который запускается в контейнере:

```bash
cd /Users/zhozhyr/PycharmProjects/gazprom
docker compose up -d --build
```

Если меняются миграции или стартовая конфигурация и нужно начать с чистой БД:

```bash
docker compose down -v
docker compose up -d --build
```

## API-контракты

- Для lifecycle лучше использовать явные бизнес-endpoints вроде `submit`, `approve`, `reject`.
- `PATCH` и `DELETE` должны уважать бизнес-ограничения статусов.
- Новые read endpoints должны отражаться в Postman-коллекции.

## Документация

При изменении API или pipeline обновляйте:

- [README.md](/Users/zhozhyr/PycharmProjects/gazprom/README.md)
- [permit-api-service.postman_collection.json](/Users/zhozhyr/PycharmProjects/gazprom/services/api_service/tools/postman/permit-api-service.postman_collection.json)
- при необходимости `README.md` конкретного сервиса
