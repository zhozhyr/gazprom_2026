from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PermitStatus


class Permit(Base):
    __tablename__ = "permits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text())
    status: Mapped[PermitStatus] = mapped_column(
        SqlEnum(PermitStatus),
        default=PermitStatus.draft,
    )
    safety_measures: Mapped[str] = mapped_column(Text())

    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    work_type_id: Mapped[int] = mapped_column(ForeignKey("work_types.id"))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))

    facility = relationship("Facility", back_populates="permits")
    work_type = relationship("WorkType", back_populates="permits")
    created_by = relationship(
        "Employee",
        back_populates="created_permits",
        foreign_keys=[created_by_id],
    )
    approvals = relationship(
        "PermitApproval",
        back_populates="permit",
        cascade="all, delete-orphan",
    )
    status_history = relationship(
        "PermitStatusHistory",
        back_populates="permit",
        cascade="all, delete-orphan",
    )
