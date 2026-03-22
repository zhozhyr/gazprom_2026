from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.employee import Employee
from app.models.facility import Facility
from app.models.work_type import WorkType
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.schemas.facility import FacilityCreate, FacilityRead
from app.schemas.permit import PermitAction, PermitCreate, PermitRead
from app.schemas.work_type import WorkTypeCreate, WorkTypeRead
from app.services.permit_service import PermitService

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/facilities", response_model=FacilityRead, status_code=status.HTTP_201_CREATED)
async def create_facility(payload: FacilityCreate, session: AsyncSession = Depends(get_session)) -> Facility:
    facility = Facility(**payload.model_dump())
    session.add(facility)
    await session.commit()
    await session.refresh(facility)
    return facility


@router.get("/facilities", response_model=list[FacilityRead])
async def list_facilities(session: AsyncSession = Depends(get_session)) -> list[Facility]:
    result = await session.execute(select(Facility).order_by(Facility.id.desc()))
    return list(result.scalars().all())


@router.post("/employees", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, session: AsyncSession = Depends(get_session)) -> Employee:
    employee = Employee(**payload.model_dump())
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


@router.get("/employees", response_model=list[EmployeeRead])
async def list_employees(session: AsyncSession = Depends(get_session)) -> list[Employee]:
    result = await session.execute(select(Employee).order_by(Employee.id.desc()))
    return list(result.scalars().all())


@router.post("/work-types", response_model=WorkTypeRead, status_code=status.HTTP_201_CREATED)
async def create_work_type(payload: WorkTypeCreate, session: AsyncSession = Depends(get_session)) -> WorkType:
    work_type = WorkType(**payload.model_dump())
    session.add(work_type)
    await session.commit()
    await session.refresh(work_type)
    return work_type


@router.get("/work-types", response_model=list[WorkTypeRead])
async def list_work_types(session: AsyncSession = Depends(get_session)) -> list[WorkType]:
    result = await session.execute(select(WorkType).order_by(WorkType.id.desc()))
    return list(result.scalars().all())


@router.post("/permits", response_model=PermitRead, status_code=status.HTTP_201_CREATED)
async def create_permit(payload: PermitCreate, session: AsyncSession = Depends(get_session)) -> PermitRead:
    service = PermitService(session)
    return await service.create_permit(payload)


@router.get("/permits", response_model=list[PermitRead])
async def list_permits(session: AsyncSession = Depends(get_session)) -> list[PermitRead]:
    service = PermitService(session)
    return await service.list_permits()


@router.get("/permits/{permit_id}", response_model=PermitRead)
async def get_permit(permit_id: int, session: AsyncSession = Depends(get_session)) -> PermitRead:
    service = PermitService(session)
    return await service.get_permit(permit_id)


@router.post("/permits/{permit_id}/submit", response_model=PermitRead)
async def submit_permit(permit_id: int, session: AsyncSession = Depends(get_session)) -> PermitRead:
    service = PermitService(session)
    return await service.submit_permit(permit_id)


@router.post("/permits/{permit_id}/approve", response_model=PermitRead)
async def approve_permit(
    permit_id: int,
    payload: PermitAction,
    session: AsyncSession = Depends(get_session),
) -> PermitRead:
    service = PermitService(session)
    return await service.approve_permit(permit_id, payload)


@router.post("/permits/{permit_id}/reject", response_model=PermitRead)
async def reject_permit(
    permit_id: int,
    payload: PermitAction,
    session: AsyncSession = Depends(get_session),
) -> PermitRead:
    service = PermitService(session)
    return await service.reject_permit(permit_id, payload)
