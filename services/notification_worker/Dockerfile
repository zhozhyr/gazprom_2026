FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV POETRY_VERSION=2.2.1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

COPY services/notification_worker/pyproject.toml ./pyproject.toml
RUN poetry install --only main

COPY services/notification_worker/src ./src

CMD ["python", "-m", "app.main"]
