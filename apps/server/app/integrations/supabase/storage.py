"""Supabase Storage 어댑터.

업로드된 카카오톡 .txt 파일은 여기에 보관한다. 추후 S3 로 갈아끼울 때를 대비해
인터페이스만 노출.
"""

from __future__ import annotations

from app.core.config import settings
from app.integrations.supabase.client import get_supabase_admin


class SupabaseStorage:
    def __init__(self, bucket: str | None = None) -> None:
        self.bucket = bucket or settings.SUPABASE_STORAGE_BUCKET
        self._client = get_supabase_admin()

    async def upload_bytes(self, *, key: str, data: bytes, content_type: str) -> str:
        """경로(key) 기준 파일 업로드. (스켈레톤)"""
        # TODO: self._client.storage.from_(self.bucket).upload(...)
        raise NotImplementedError

    async def get_public_url(self, key: str) -> str:
        # TODO
        raise NotImplementedError
