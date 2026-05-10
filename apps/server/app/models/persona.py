"""Persona 모델 — 사용자가 만든 가상 AI 페르소나."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPKMixin


class Persona(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "personas"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(40), nullable=False)
    personality: Mapped[str | None] = mapped_column(Text)
    speaking_style: Mapped[str | None] = mapped_column(Text)
    profile_image_url: Mapped[str | None] = mapped_column(String(1024))
    safety_notes: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="personas")  # noqa: F821
