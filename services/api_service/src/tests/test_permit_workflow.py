import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.employee import Employee
from app.models.facility import Facility
from app.models.work_type import WorkType
from app.schemas.permit import PermitAction, PermitCreate
from app.services.permit_service import PermitService


async def create_session_factory() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return session_factory


async def seed_reference_data(session: AsyncSession) -> None:
    session.add_all(
        [
            Facility(name="GRS-1", facility_type="gas_distribution_station", location="Moscow region"),
            WorkType(name="Hot work", risk_level="critical", description="Welding and flame work"),
            Employee(full_name="Ivan Petrov", role="Initiator", department="Operations"),
            Employee(full_name="Anna Sidorova", role="Safety Engineer", department="HSE"),
            Employee(full_name="Petr Smirnov", role="Shift Lead", department="Operations"),
        ]
    )
    await session.commit()


def build_permit_payload(**overrides: int | str) -> PermitCreate:
    payload: dict[str, int | str] = {
        "title": "Pipeline welding",
        "description": "Repair welding on line 4",
        "safety_measures": "Gas analysis, barriers, extinguishers",
        "facility_id": 1,
        "work_type_id": 1,
        "created_by_id": 1,
        "approver_employee_id": 2,
    }
    payload.update(overrides)
    return PermitCreate(**payload)


@pytest.mark.asyncio
async def test_permit_workflow_create_submit_approve(monkeypatch: pytest.MonkeyPatch) -> None:
    session_factory = await create_session_factory()

    published_events: list[tuple[str, dict[str, object]]] = []

    async def fake_publish(topic: str, payload: dict[str, object]) -> None:
        published_events.append((topic, payload))

    monkeypatch.setattr("app.services.permit_service.event_publisher.publish", fake_publish)

    async with session_factory() as session:
        await seed_reference_data(session)

        service = PermitService(session)
        permit = await service.create_permit(build_permit_payload())
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


@pytest.mark.asyncio
async def test_permit_workflow_reject(monkeypatch: pytest.MonkeyPatch) -> None:
    session_factory = await create_session_factory()
    published_events: list[tuple[str, dict[str, object]]] = []

    async def fake_publish(topic: str, payload: dict[str, object]) -> None:
        published_events.append((topic, payload))

    monkeypatch.setattr("app.services.permit_service.event_publisher.publish", fake_publish)

    async with session_factory() as session:
        await seed_reference_data(session)
        service = PermitService(session)
        permit = await service.create_permit(build_permit_payload())

        await service.submit_permit(permit.id)
        rejected = await service.reject_permit(
            permit.id,
            PermitAction(approver_employee_id=2, comment="Missing ventilation checklist"),
        )

        assert rejected.status.value == "rejected"
        assert rejected.approvals[0].status.value == "rejected"
        assert rejected.status_history[-1].note == "Missing ventilation checklist"

    assert [topic for topic, _ in published_events] == ["permits.submitted", "permits.reviewed"]


@pytest.mark.asyncio
async def test_submit_non_draft_permit_raises_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    session_factory = await create_session_factory()

    async def fake_publish(topic: str, payload: dict[str, object]) -> None:
        return None

    monkeypatch.setattr("app.services.permit_service.event_publisher.publish", fake_publish)

    async with session_factory() as session:
        await seed_reference_data(session)
        service = PermitService(session)
        permit = await service.create_permit(build_permit_payload())
        await service.submit_permit(permit.id)

        with pytest.raises(HTTPException) as exc_info:
            await service.submit_permit(permit.id)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Only draft permits can be submitted"


@pytest.mark.asyncio
async def test_create_permit_with_missing_reference_raises_not_found() -> None:
    session_factory = await create_session_factory()

    async with session_factory() as session:
        await seed_reference_data(session)
        service = PermitService(session)

        with pytest.raises(HTTPException) as exc_info:
            await service.create_permit(build_permit_payload(facility_id=999))

    assert exc_info.value.status_code == 404
    assert "Facility#999" in exc_info.value.detail


@pytest.mark.asyncio
async def test_approve_with_wrong_employee_raises_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    session_factory = await create_session_factory()

    async def fake_publish(topic: str, payload: dict[str, object]) -> None:
        return None

    monkeypatch.setattr("app.services.permit_service.event_publisher.publish", fake_publish)

    async with session_factory() as session:
        await seed_reference_data(session)
        service = PermitService(session)
        permit = await service.create_permit(build_permit_payload())
        await service.submit_permit(permit.id)

        with pytest.raises(HTTPException) as exc_info:
            await service.approve_permit(
                permit.id,
                PermitAction(approver_employee_id=3, comment="Attempt from wrong approver"),
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Approval step not found for employee"
