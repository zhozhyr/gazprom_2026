# Notification Worker

Kafka worker для записи уведомлений по жизненному циклу permit.

## Что делает

- слушает `permits.submitted`
- слушает `permits.compliance_passed`
- слушает `permits.compliance_failed`
- сохраняет запись в таблицу `notifications`
