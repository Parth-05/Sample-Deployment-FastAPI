from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Text, ForeignKey
from app.db.base import Base

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    fitness_goal: Mapped[Optional[str]] = mapped_column(Text)

    profile = relationship("Profile", back_populates="client", uselist=False)
