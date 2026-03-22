FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.2.1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

COPY services/api_service/pyproject.toml ./pyproject.toml
RUN poetry install --only main

COPY services/api_service/alembic.ini ./alembic.ini
COPY services/api_service/migrations ./migrations
COPY services/api_service/src ./src

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000"]
