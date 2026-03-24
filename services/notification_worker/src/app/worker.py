import logging

from app.db.session import SessionLocal
from app.services.kafka_consumer import KafkaEventConsumer
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class NotificationWorker:
    def __init__(self) -> None:
        self.consumer = KafkaEventConsumer()

    async def run(self) -> None:
        await self.consumer.start()
        try:
            async for message in self.consumer.consumer:
                await self.process_message(message.topic, message.value)
        finally:
            await self.consumer.stop()

    async def process_message(self, topic: str, payload: dict[str, object]) -> None:
        async with SessionLocal() as session:
            service = NotificationService(session)
            notification = await service.handle_event(topic, payload)
            logger.info(
                "Stored notification %s for permit %s",
                notification.id,
                notification.permit_id,
            )
