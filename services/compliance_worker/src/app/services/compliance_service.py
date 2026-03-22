from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import PermitStatus
from app.models.permit import Permit
from app.models.permit_status_history import PermitStatusHistory


@dataclass
class ComplianceResult:
    permit: Permit | None
    passed: bool
    reason: str


class ComplianceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def process_submitted_permit(self, permit_id: int) -> ComplianceResult:
        result = await self.session.execute(
            select(Permit)
            .where(Permit.id == permit_id)
            .options(selectinload(Permit.approvals), selectinload(Permit.status_history))
        )
        permit = result.scalar_one_or_none()
        if permit is None:
            return ComplianceResult(permit=None, passed=False, reason="Permit not found")

        if permit.status != PermitStatus.submitted:
            return ComplianceResult(permit=permit, passed=False, reason=f"Permit status is {permit.status.value}")

        reasons: list[str] = []
        if not permit.safety_measures.strip():
            reasons.append("safety_measures must not be empty")
        if not permit.approvals:
            reasons.append("permit must have at least one approval step")

        if reasons:
            permit.status = PermitStatus.rejected
            reason = "; ".join(reasons)
            permit.status_history.append(
                PermitStatusHistory(
                    status=PermitStatus.rejected,
                    note=f"Compliance failed: {reason}",
                )
            )
            await self.session.commit()
            await self.session.refresh(permit)
            return ComplianceResult(permit=permit, passed=False, reason=reason)

        return ComplianceResult(permit=permit, passed=True, reason="Compliance passed")
