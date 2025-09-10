from uuid import uuid4
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM as PGEnum
from sqlalchemy import Text, Boolean, text
from app.db.base import Base
from app.models.enums import UserRole

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )

    name: Mapped[Optional[str]] = mapped_column("full_name", Text)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    password: Mapped[Optional[str]] = mapped_column(Text)        
    phone: Mapped[Optional[str]] = mapped_column(Text)

    # IMPORTANT: bind to existing Postgres enum type
    user_type: Mapped[Optional[UserRole]] = mapped_column(
        "role",
        PGEnum(UserRole, name="user_role", create_type=False),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column("onboarded", Boolean, nullable=False, server_default=text("false"))

    trainer: Mapped[Optional["Trainer"]] = relationship(back_populates="profile", uselist=False)
    client:  Mapped[Optional["Client"]]  = relationship(back_populates="profile", uselist=False)
