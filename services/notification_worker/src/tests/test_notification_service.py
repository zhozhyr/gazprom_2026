import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.notification import Notification
from app.services.notification_service import NotificationService


@pytest.mark.asyncio
async def test_handle_compliance_failed_event_creates_notification() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        service = NotificationService(session)
        notification = await service.handle_event(
            "permits.compliance_failed",
            {"permit_id": 12, "result": "failed", "reason": "safety_measures must not be empty"},
        )

        assert notification.permit_id == 12
        assert "failed compliance" in notification.message

        result = await session.execute(select(Notification))
        records = list(result.scalars().all())
        assert len(records) == 1
        assert records[0].event_type == "permits.compliance_failed"
