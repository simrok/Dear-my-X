"""MemoryChunk — 임베딩된 대화 조각 (RAG 검색 대상)."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPKMixin
from app.db.pgvector import EmbeddingVector


class MemoryChunk(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "memory_chunks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    persona_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personas.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    speaker: Mapped[str | None] = mapped_column(String(80))
    source: Mapped[str | None] = mapped_column(String(255))

    # pgvector 컬럼. 인덱스(IVFFlat / HNSW) 는 alembic 에서 생성한다.
    embedding: Mapped[list[float]] = mapped_column(EmbeddingVector, nullable=False)
