from pydantic import BaseModel

from app.schemas.common import ORMModel


class FacilityCreate(BaseModel):
    name: str
    facility_type: str
    location: str


class FacilityRead(ORMModel):
    id: int
    name: str
    facility_type: str
    location: str
