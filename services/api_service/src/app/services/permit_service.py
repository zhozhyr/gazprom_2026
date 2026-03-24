from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.employee import Employee
from app.models.enums import ApprovalStatus, PermitStatus
from app.models.facility import Facility
from app.models.permit import Permit
from app.models.permit_approval import PermitApproval
from app.models.permit_status_history import PermitStatusHistory
from app.models.work_type import WorkType
from app.repositories.permit_repository import PermitRepository
from app.schemas.permit import PermitAction, PermitCreate
from app.services.event_publisher import event_publisher


class PermitService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = PermitRepository(session)

    async def list_permits(self) -> list[Permit]:
        return await self.repository.list_all()

    async def get_permit(self, permit_id: int) -> Permit:
        permit = await self.repository.get_by_id(permit_id)
        if permit is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permit not found")
        return permit

    async def create_permit(self, payload: PermitCreate) -> Permit:
        await self._ensure_refs_exist(
            payload.facility_id,
            payload.work_type_id,
            payload.created_by_id,
            payload.approver_employee_id,
        )

        permit = Permit(
            title=payload.title,
            description=payload.description,
            safety_measures=payload.safety_measures,
            facility_id=payload.facility_id,
            work_type_id=payload.work_type_id,
            created_by_id=payload.created_by_id,
            status=PermitStatus.draft,
            approvals=[
                PermitApproval(
                    approver_employee_id=payload.approver_employee_id,
                    status=ApprovalStatus.pending,
                    comment="",
                )
            ],
            status_history=[PermitStatusHistory(status=PermitStatus.draft, note="Permit created")],
        )
        await self.repository.add(permit)
        await self.session.commit()
        return await self.get_permit(permit.id)

    async def submit_permit(self, permit_id: int) -> Permit:
        permit = await self.get_permit(permit_id)
        if permit.status != PermitStatus.draft:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft permits can be submitted",
            )

        permit.status = PermitStatus.submitted
        permit.status_history.append(
            PermitStatusHistory(status=PermitStatus.submitted, note="Permit submitted for review")
        )
        await self.session.commit()
        await event_publisher.publish(
            settings.kafka_topic_permit_submitted,
            {"permit_id": permit.id, "status": permit.status.value},
        )
        return await self.get_permit(permit.id)

    async def approve_permit(self, permit_id: int, payload: PermitAction) -> Permit:
        permit = await self.get_permit(permit_id)
        if permit.status not in {PermitStatus.submitted, PermitStatus.under_review}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permit is not awaiting approval",
            )

        approval = self._get_approval_for_employee(permit, payload.approver_employee_id)
        approval.status = ApprovalStatus.approved
        approval.comment = payload.comment
        permit.status = PermitStatus.approved
        permit.status_history.append(
            PermitStatusHistory(
                status=PermitStatus.approved,
                note=payload.comment or "Permit approved",
            )
        )
        await self.session.commit()
        await event_publisher.publish(
            settings.kafka_topic_permit_reviewed,
            {
                "permit_id": permit.id,
                "approval_status": approval.status.value,
                "approver_employee_id": payload.approver_employee_id,
            },
        )
        return await self.get_permit(permit.id)

    async def reject_permit(self, permit_id: int, payload: PermitAction) -> Permit:
        permit = await self.get_permit(permit_id)
        if permit.status not in {PermitStatus.submitted, PermitStatus.under_review}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Permit is not awaiting approval",
            )

        approval = self._get_approval_for_employee(permit, payload.approver_employee_id)
        approval.status = ApprovalStatus.rejected
        approval.comment = payload.comment
        permit.status = PermitStatus.rejected
        permit.status_history.append(
            PermitStatusHistory(
                status=PermitStatus.rejected,
                note=payload.comment or "Permit rejected",
            )
        )
        await self.session.commit()
        await event_publisher.publish(
            settings.kafka_topic_permit_reviewed,
            {
                "permit_id": permit.id,
                "approval_status": approval.status.value,
                "approver_employee_id": payload.approver_employee_id,
            },
        )
        return await self.get_permit(permit.id)

    async def _ensure_refs_exist(
        self,
        facility_id: int,
        work_type_id: int,
        created_by_id: int,
        approver_employee_id: int,
    ) -> None:
        for model, value in (
            (Facility, facility_id),
            (WorkType, work_type_id),
            (Employee, created_by_id),
            (Employee, approver_employee_id),
        ):
            result = await self.session.execute(select(model).where(model.id == value))
            if result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Referenced entity not found: {model.__name__}#{value}",
                )

    @staticmethod
    def _get_approval_for_employee(permit: Permit, approver_employee_id: int) -> PermitApproval:
        for approval in permit.approvals:
            if approval.approver_employee_id == approver_employee_id:
                return approval
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval step not found for employee",
        )
