import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.enums import PermitStatus
from app.models.permit import Permit
from app.models.permit_status_history import PermitStatusHistory
from app.services.approval_service import ApprovalService


@pytest.mark.asyncio
async def test_process_submitted_permit_moves_to_under_review() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        permit = Permit(
            title="Valve maintenance",
            description="Scheduled maintenance on valve 7",
            status=PermitStatus.submitted,
            safety_measures="LOTO, gas detector",
            facility_id=1,
            work_type_id=1,
            created_by_id=1,
            status_history=[PermitStatusHistory(status=PermitStatus.submitted, note="Submitted by API")],
        )
        session.add(permit)
        await session.commit()

        service = ApprovalService(session)
        updated = await service.process_submitted_permit(permit.id)

        assert updated is not None
        assert updated.status == PermitStatus.under_review

        result = await session.execute(select(Permit).where(Permit.id == permit.id))
        persisted = result.scalar_one()
        assert persisted.status == PermitStatus.under_review


@pytest.mark.asyncio
async def test_process_submitted_permit_ignores_non_submitted_status() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        permit = Permit(
            title="Compressor inspection",
            description="Inspection before shift",
            status=PermitStatus.approved,
            safety_measures="Checklist completed",
            facility_id=1,
            work_type_id=1,
            created_by_id=1,
            status_history=[PermitStatusHistory(status=PermitStatus.approved, note="Already approved")],
        )
        session.add(permit)
        await session.commit()

        service = ApprovalService(session)
        unchanged = await service.process_submitted_permit(permit.id)

        assert unchanged is not None
        assert unchanged.status == PermitStatus.approved
