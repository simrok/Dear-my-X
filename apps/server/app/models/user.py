"""User 모델.

Supabase Auth 가 권위 있는 ID 를 발급하므로, `id` 는 Supabase 의 UUID 를 그대로 사용한다.
"""

from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)

    # 관계 (필요해질 때 lazy=raise 등으로 조정)
    personas: Mapped[list["Persona"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )
