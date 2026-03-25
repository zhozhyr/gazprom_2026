from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PermitStatus


class PermitStatusHistory(Base):
    __tablename__ = "permit_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(ForeignKey("permits.id"))
    status: Mapped[PermitStatus] = mapped_column(SqlEnum(PermitStatus))
    note: Mapped[str] = mapped_column(String(500), default="")

    permit = relationship("Permit", back_populates="status_history")
