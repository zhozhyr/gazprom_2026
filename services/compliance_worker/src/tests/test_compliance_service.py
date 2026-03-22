import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models.enums import ApprovalStatus, PermitStatus
from app.models.permit import Permit
from app.models.permit_approval import PermitApproval
from app.models.permit_status_history import PermitStatusHistory
from app.services.compliance_service import ComplianceService


@pytest.mark.asyncio
async def test_compliance_passes_when_safety_measures_and_approval_exist() -> None:
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
            approvals=[
                PermitApproval(
                    approver_employee_id=2,
                    status=ApprovalStatus.pending,
                    comment="",
                )
            ],
            status_history=[PermitStatusHistory(status=PermitStatus.submitted, note="Submitted by API")],
        )
        session.add(permit)
        await session.commit()

        service = ComplianceService(session)
        result = await service.process_submitted_permit(permit.id)

        assert result.passed is True
        assert result.reason == "Compliance passed"


@pytest.mark.asyncio
async def test_compliance_fails_and_rejects_permit_when_safety_measures_empty() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        permit = Permit(
            title="Hot work",
            description="Repair work",
            status=PermitStatus.submitted,
            safety_measures="   ",
            facility_id=1,
            work_type_id=1,
            created_by_id=1,
            approvals=[],
            status_history=[PermitStatusHistory(status=PermitStatus.submitted, note="Submitted by API")],
        )
        session.add(permit)
        await session.commit()

        service = ComplianceService(session)
        result = await service.process_submitted_permit(permit.id)

        assert result.passed is False
        assert "safety_measures must not be empty" in result.reason
        assert "at least one approval step" in result.reason
        assert result.permit is not None
        assert result.permit.status == PermitStatus.rejected
