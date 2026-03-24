from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ApprovalStatus


class PermitApproval(Base):
    __tablename__ = "permit_approvals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(ForeignKey("permits.id"))
    approver_employee_id: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(SqlEnum(ApprovalStatus), nullable=False)
    comment: Mapped[str] = mapped_column(String(500), default="")

    permit = relationship("Permit", back_populates="approvals")
