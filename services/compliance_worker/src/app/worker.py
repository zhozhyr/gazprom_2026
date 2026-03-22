import logging

from app.config import settings
from app.db.session import SessionLocal
from app.services.compliance_service import ComplianceService
from app.services.event_publisher import EventPublisher
from app.services.kafka_consumer import KafkaEventConsumer

logger = logging.getLogger(__name__)


class ComplianceWorker:
    def __init__(self) -> None:
        self.consumer = KafkaEventConsumer()
        self.publisher = EventPublisher()

    async def run(self) -> None:
        await self.consumer.start()
        await self.publisher.start()
        try:
            async for message in self.consumer.consumer:
                await self.process_message(message.value)
        finally:
            await self.consumer.stop()
            await self.publisher.stop()

    async def process_message(self, payload: dict[str, object]) -> None:
        permit_id = int(payload["permit_id"])
        async with SessionLocal() as session:
            service = ComplianceService(session)
            result = await service.process_submitted_permit(permit_id)

        if result.permit is None:
            logger.warning("Permit %s not found for compliance check", permit_id)
            return

        if result.passed:
            await self.publisher.publish(
                settings.kafka_topic_compliance_passed,
                {"permit_id": permit_id, "result": "passed"},
            )
            logger.info("Permit %s passed compliance", permit_id)
            return

        await self.publisher.publish(
            settings.kafka_topic_compliance_failed,
            {"permit_id": permit_id, "result": "failed", "reason": result.reason},
        )
        logger.info("Permit %s failed compliance: %s", permit_id, result.reason)
