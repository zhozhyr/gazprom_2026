from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.permit import Permit


class PermitRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, permit: Permit) -> Permit:
        self.session.add(permit)
        await self.session.flush()
        await self.session.refresh(permit)
        return permit

    async def get_by_id(self, permit_id: int) -> Permit | None:
        stmt = (
            select(Permit)
            .where(Permit.id == permit_id)
            .options(
                selectinload(Permit.facility),
                selectinload(Permit.work_type),
                selectinload(Permit.created_by),
                selectinload(Permit.approvals),
                selectinload(Permit.status_history),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Permit]:
        stmt = (
            select(Permit)
            .order_by(Permit.id.desc())
            .options(
                selectinload(Permit.facility),
                selectinload(Permit.work_type),
                selectinload(Permit.created_by),
                selectinload(Permit.approvals),
                selectinload(Permit.status_history),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
