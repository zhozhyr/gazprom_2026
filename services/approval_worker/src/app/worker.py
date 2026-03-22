import logging

from app.db.session import SessionLocal
from app.services.approval_service import ApprovalService
from app.services.kafka_consumer import KafkaEventConsumer

logger = logging.getLogger(__name__)


class ApprovalWorker:
    def __init__(self) -> None:
        self.consumer = KafkaEventConsumer()

    async def run(self) -> None:
        await self.consumer.start()
        try:
            async for message in self.consumer.consumer:
                await self.process_message(message.value)
        finally:
            await self.consumer.stop()

    async def process_message(self, payload: dict[str, object]) -> None:
        permit_id = int(payload["permit_id"])
        async with SessionLocal() as session:
            service = ApprovalService(session)
            permit = await service.process_submitted_permit(permit_id)
            if permit is None:
                logger.warning("Permit %s not found", permit_id)
                return
            logger.info("Permit %s status is now %s", permit.id, permit.status.value)
