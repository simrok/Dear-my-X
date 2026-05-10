"""MemoryChunk repository — pgvector 유사도 검색 포함."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.memory_chunk import MemoryChunk
from app.repositories.base import BaseRepository


class MemoryChunkRepository(BaseRepository[MemoryChunk]):
    model = MemoryChunk

    async def bulk_create(
        self,
        *,
        rows: list[dict],
    ) -> int:
        """대량 insert. 트랜잭션 commit 은 호출자가 결정."""
        if not rows:
            return 0
        objs = [MemoryChunk(**r) for r in rows]
        self.session.add_all(objs)
        await self.session.flush()
        return len(objs)

    async def search_similar(
        self,
        *,
        persona_id: uuid.UUID,
        query_embedding: list[float],
        top_k: int = 8,
    ) -> list[MemoryChunk]:
        """코사인 거리 기준 top-k 유사 chunk."""
        # pgvector 의 `<=>` 가 코사인 거리, `<#>` 가 내적, `<->` 가 L2.
        # MemoryChunk.embedding.cosine_distance(...) 헬퍼는 pgvector.sqlalchemy 가 제공.
        stmt = (
            select(MemoryChunk)
            .where(MemoryChunk.persona_id == persona_id)
            .order_by(MemoryChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
