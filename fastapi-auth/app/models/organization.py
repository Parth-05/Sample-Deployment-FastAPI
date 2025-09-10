# app/models/organization.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    org_id: Mapped[str] = mapped_column(
        "org_id",
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    # one organization → many trainers
    trainers: Mapped[List["Trainer"]] = relationship(
        back_populates="organization",
        passive_deletes=True,   
    )
