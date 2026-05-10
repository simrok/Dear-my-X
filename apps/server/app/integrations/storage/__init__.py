"""Storage 추상 — Supabase / S3 / 로컬 디스크 등 교체 가능한 인터페이스."""

from typing import Protocol


class ObjectStorage(Protocol):
    async def upload_bytes(self, *, key: str, data: bytes, content_type: str) -> str: ...
    async def get_public_url(self, key: str) -> str: ...
