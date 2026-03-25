from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(100))
    department: Mapped[str] = mapped_column(String(100))

    created_permits = relationship(
        "Permit",
        back_populates="created_by",
        foreign_keys="Permit.created_by_id",
    )
    approvals = relationship("PermitApproval", back_populates="approver")
