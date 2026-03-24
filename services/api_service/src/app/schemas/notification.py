from app.schemas.common import ORMModel


class NotificationRead(ORMModel):
    id: int
    permit_id: int
    event_type: str
    message: str
    payload: dict[str, object]
