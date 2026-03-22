# Approval Worker

Kafka worker, который слушает `permits.compliance_passed` и переводит наряд в статус `under_review`.

## Запуск

```bash
cd services/approval_worker
poetry install
poetry run python -m app.main
```
