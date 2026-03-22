from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    facility_type: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(255))

    permits = relationship("Permit", back_populates="facility")
