from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def handle_event(self, topic: str, payload: dict[str, object]) -> Notification:
        permit_id = int(cast(int | str, payload["permit_id"]))
        notification = Notification(
            permit_id=permit_id,
            event_type=topic,
            message=self._build_message(topic, payload),
            payload=payload,
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    def _build_message(self, topic: str, payload: dict[str, object]) -> str:
        if topic.endswith("submitted"):
            return f"Permit #{payload['permit_id']} was submitted."
        if topic.endswith("compliance_passed"):
            return f"Permit #{payload['permit_id']} passed compliance checks."
        if topic.endswith("compliance_failed"):
            reason = payload.get("reason", "unknown reason")
            return f"Permit #{payload['permit_id']} failed compliance: {reason}."
        return f"Permit #{payload['permit_id']} event received."
