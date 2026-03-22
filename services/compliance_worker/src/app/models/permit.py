from sqlalchemy import Integer, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PermitStatus


class Permit(Base):
    __tablename__ = "permits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[PermitStatus] = mapped_column(SqlEnum(PermitStatus), nullable=False)
    safety_measures: Mapped[str] = mapped_column(Text(), nullable=False)
    facility_id: Mapped[int] = mapped_column(Integer, nullable=False)
    work_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by_id: Mapped[int] = mapped_column(Integer, nullable=False)

    approvals = relationship("PermitApproval", back_populates="permit", cascade="all, delete-orphan")
    status_history = relationship("PermitStatusHistory", back_populates="permit", cascade="all, delete-orphan")
