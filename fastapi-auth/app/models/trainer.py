# app/models/trainer.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Trainer(Base):
    __tablename__ = "trainers"

    # PK is also FK → profiles.id
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    bio: Mapped[Optional[str]] = mapped_column(Text)
    certifications: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text))

    # keep nullable=True if you want it optional in DB
    years_exp: Mapped[Optional[int]] = mapped_column(nullable=True)

    # nullable FK to organizations.org_id
    organization_id: Mapped[Optional[str]] = mapped_column(
        "org_id",
        UUID(as_uuid=False),
        ForeignKey("organizations.org_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    profile = relationship("Profile", back_populates="trainer", uselist=False)

    # many trainers → one organization
    organization = relationship("Organization", back_populates="trainers")
