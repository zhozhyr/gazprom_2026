from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WorkType(Base):
    __tablename__ = "work_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    risk_level: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))

    permits = relationship("Permit", back_populates="work_type")
