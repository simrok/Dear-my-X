"""임베딩 어댑터 (기본: OpenAI text-embedding-3-small).

추후 다른 제공자 (Voyage 등) 추가 시 동일 Protocol 을 구현해 교체 가능.
"""

from __future__ import annotations

from typing import Protocol

from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings


class EmbeddingClient(Protocol):
    @property
    def dimensions(self) -> int: ...
    async def embed(self, text: str) -> list[float]: ...
    async def embed_many(self, texts: list[str]) -> list[list[float]]: ...


class EmbeddingError(Exception):
    pass


# OpenAI Embedding API 의 단일 요청 입력 한도. (model 별 상이; 안전치)
_BATCH_SIZE = 100


class OpenAIEmbeddingClient:
    """OpenAI text-embedding-3-* 어댑터."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        dimensions: int | None = None,
    ) -> None:
        self._api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBEDDING_MODEL
        self._dimensions = dimensions or settings.EMBEDDING_DIMENSIONS
        # API 키가 없어도 인스턴스 자체는 만들 수 있게 (dev 환경).
        # 실제 호출 시 401 이 나도록 OpenAI SDK 에 위임.
        self._client = AsyncOpenAI(api_key=self._api_key) if self._api_key else None

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def embed(self, text: str) -> list[float]:
        result = await self.embed_many([text])
        return result[0]

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._client is None:
            raise EmbeddingError("OPENAI_API_KEY is not configured")

        out: list[list[float]] = []
        for i in range(0, len(texts), _BATCH_SIZE):
            batch = texts[i : i + _BATCH_SIZE]
            vecs = await self._embed_batch(batch)
            out.extend(vecs)
        return out

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        assert self._client is not None
        try:
            resp = await self._client.embeddings.create(
                model=self.model,
                input=batch,
                # text-embedding-3-* 는 dimensions 파라미터로 압축 가능.
                # 기본 1536 을 그대로 쓰면 굳이 보낼 필요 없음.
                # dimensions=self._dimensions,
            )
        except Exception as e:  # OpenAI / 네트워크 에러
            raise EmbeddingError(f"OpenAI embedding failed: {e}") from e

        # 응답은 입력 순서와 동일하게 정렬되어 옴
        return [item.embedding for item in resp.data]
