import json

from aiokafka import AIOKafkaConsumer

from app.config import settings


class KafkaEventConsumer:
    def __init__(self) -> None:
        self.consumer = AIOKafkaConsumer(
            settings.kafka_topic_permit_submitted,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id=settings.kafka_client_id,
            group_id=settings.kafka_group_id,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
            auto_offset_reset="earliest",
        )

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        await self.consumer.stop()
