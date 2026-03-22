import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.employee import Employee
from app.models.facility import Facility
from app.models.work_type import WorkType
from app.schemas.permit import PermitAction, PermitCreate
from app.services.permit_service import PermitService


@pytest.mark.asyncio
async def test_permit_workflow_create_submit_approve(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    published_events: list[tuple[str, dict[str, object]]] = []

    async def fake_publish(topic: str, payload: dict[str, object]) -> None:
        published_events.append((topic, payload))

    monkeypatch.setattr("app.services.permit_service.event_publisher.publish", fake_publish)

    async with session_factory() as session:
        session.add_all(
            [
                Facility(name="GRS-1", facility_type="gas_distribution_station", location="Moscow region"),
                WorkType(name="Hot work", risk_level="critical", description="Welding and flame work"),
                Employee(full_name="Ivan Petrov", role="Initiator", department="Operations"),
                Employee(full_name="Anna Sidorova", role="Safety Engineer", department="HSE"),
            ]
        )
        await session.commit()

        service = PermitService(session)
        permit = await service.create_permit(
            PermitCreate(
                title="Pipeline welding",
                description="Repair welding on line 4",
                safety_measures="Gas analysis, barriers, extinguishers",
                facility_id=1,
                work_type_id=1,
                created_by_id=1,
                approver_employee_id=2,
            )
        )
        assert permit.status.value == "draft"

        submitted = await service.submit_permit(permit.id)
        assert submitted.status.value == "submitted"

        approved = await service.approve_permit(
            permit.id,
            PermitAction(approver_employee_id=2, comment="All safety controls are in place"),
        )
        assert approved.status.value == "approved"
        assert approved.approvals[0].status.value == "approved"

    assert [topic for topic, _ in published_events] == ["permits.submitted", "permits.reviewed"]
