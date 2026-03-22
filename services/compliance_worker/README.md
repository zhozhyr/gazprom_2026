# Compliance Worker

Kafka worker, который проверяет permit после `submitted` и публикует результат compliance-проверки.

## Что делает

- слушает `permits.submitted`
- проверяет минимальные условия допуска
- публикует `permits.compliance_passed` или `permits.compliance_failed`
- при провале переводит permit в `rejected`
