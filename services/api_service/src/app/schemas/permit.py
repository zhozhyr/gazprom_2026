from pydantic import BaseModel

from app.models.enums import ApprovalStatus, PermitStatus
from app.schemas.common import ORMModel
from app.schemas.employee import EmployeeRead
from app.schemas.facility import FacilityRead
from app.schemas.work_type import WorkTypeRead


class PermitCreate(BaseModel):
    title: str
    description: str
    safety_measures: str
    facility_id: int
    work_type_id: int
    created_by_id: int
    approver_employee_id: int


class PermitAction(BaseModel):
    approver_employee_id: int
    comment: str = ""


class PermitUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    safety_measures: str | None = None
    facility_id: int | None = None
    work_type_id: int | None = None


class PermitApprovalRead(ORMModel):
    id: int
    approver_employee_id: int
    status: ApprovalStatus
    comment: str


class PermitStatusHistoryRead(ORMModel):
    id: int
    status: PermitStatus
    note: str


class PermitRead(ORMModel):
    id: int
    title: str
    description: str
    safety_measures: str
    status: PermitStatus
    facility: FacilityRead
    work_type: WorkTypeRead
    created_by: EmployeeRead
    approvals: list[PermitApprovalRead]
    status_history: list[PermitStatusHistoryRead]
