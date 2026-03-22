from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import PermitStatus
from app.models.permit import Permit
from app.models.permit_status_history import PermitStatusHistory


class ApprovalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def process_compliance_passed_permit(self, permit_id: int) -> Permit | None:
        result = await self.session.execute(
            select(Permit).where(Permit.id == permit_id).options(selectinload(Permit.status_history))
        )
        permit = result.scalar_one_or_none()
        if permit is None:
            return None

        if permit.status != PermitStatus.submitted:
            return permit

        permit.status = PermitStatus.under_review
        permit.status_history.append(
            PermitStatusHistory(
                status=PermitStatus.under_review,
                note="Permit moved to under_review by approval worker",
            )
        )
        await self.session.commit()
        await self.session.refresh(permit)
        return permit
