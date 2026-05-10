"""MemoryRetriever — 페르소나 메모리 검색기.

services 가 주입받아 사용한다. 내부적으로 EmbeddingClient + MemoryChunkRepository 를
조합해서 top-k 청크를 반환한다.
"""

from __future__ import annotations

import uuid

from app.ai.clients.embedding_client import EmbeddingClient
from app.repositories.memory_repo import MemoryChunkRepository


class MemoryRetriever:
    def __init__(
        self,
        *,
        embedder: EmbeddingClient,
        repo: MemoryChunkRepository,
    ) -> None:
        self.embedder = embedder
        self.repo = repo

    async def search(
        self,
        *,
        persona_id: uuid.UUID,
        query: str,
        top_k: int = 8,
    ) -> list[str]:
        embedding = await self.embedder.embed(query)
        chunks = await self.repo.search_similar(
            persona_id=persona_id,
            query_embedding=embedding,
            top_k=top_k,
        )
        return [c.content for c in chunks]
