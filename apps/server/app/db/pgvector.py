"""pgvector 헬퍼.

`pgvector.sqlalchemy.Vector` 타입을 가져와 모델에서 일관되게 사용하기 위한 얇은 래퍼.
모델에서는 `Vector(EMBEDDING_DIMENSIONS)` 처럼 사용한다.
"""

from __future__ import annotations

from pgvector.sqlalchemy import Vector

from app.core.config import settings

EmbeddingVector = Vector(settings.EMBEDDING_DIMENSIONS)

__all__ = ["EmbeddingVector", "Vector"]
