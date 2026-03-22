from pydantic import BaseModel

from app.schemas.common import ORMModel


class EmployeeCreate(BaseModel):
    full_name: str
    role: str
    department: str


class EmployeeRead(ORMModel):
    id: int
    full_name: str
    role: str
    department: str
