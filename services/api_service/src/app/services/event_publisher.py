import json
import logging
from collections.abc import Mapping
from contextlib import suppress

from aiokafka import AIOKafkaProducer

from app.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if not settings.kafka_enabled or self._producer is not None:
            return
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id=settings.kafka_client_id,
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer is None:
            return
        with suppress(Exception):
            await self._producer.stop()
        self._producer = None

    async def publish(self, topic: str, payload: Mapping[str, object]) -> None:
        if not settings.kafka_enabled:
            logger.info("Kafka disabled, skipped event for topic %s: %s", topic, payload)
            return
        if self._producer is None:
            await self.start()
        assert self._producer is not None
        await self._producer.send_and_wait(topic, dict(payload))


event_publisher = EventPublisher()
