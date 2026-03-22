import json
from collections.abc import Mapping

from aiokafka import AIOKafkaProducer

from app.config import settings


class EventPublisher:
    def __init__(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id=settings.kafka_client_id,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def publish(self, topic: str, payload: Mapping[str, object]) -> None:
        await self._producer.send_and_wait(topic, dict(payload))
