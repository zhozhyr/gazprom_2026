from pydantic import BaseModel

from app.schemas.common import ORMModel


class WorkTypeCreate(BaseModel):
    name: str
    risk_level: str
    description: str


class WorkTypeRead(ORMModel):
    id: int
    name: str
    risk_level: str
    description: str
