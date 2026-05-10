"""LocalStorage — 개발용 디스크 기반 ObjectStorage 어댑터.

Supabase Storage 가 셋업되기 전에 동일 인터페이스로 쓸 수 있게 한 임시 구현.
운영에서는 `integrations/supabase/storage.py` 의 `SupabaseStorage` 로 교체.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


class LocalStorage:
    """파일을 OS 임시 디렉터리(`/tmp/dear_my_x/uploads`) 에 저장."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base = Path(base_dir or os.path.join(tempfile.gettempdir(), "dear_my_x", "uploads"))
        self.base.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # key 가 슬래시로 시작해도 안전하게 처리
        return self.base / key.lstrip("/")

    async def upload_bytes(self, *, key: str, data: bytes, content_type: str) -> str:
        # content_type 은 디스크 저장에서 사용하지 않음 (인터페이스 호환만 유지)
        del content_type
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return f"local://{p}"

    async def get_public_url(self, key: str) -> str:
        return f"local://{self._path(key)}"

    async def read_bytes(self, key_or_url: str) -> bytes:
        """LocalStorage 전용 헬퍼 (Protocol 외) — 다시 읽어올 때 사용."""
        if key_or_url.startswith("local://"):
            p = Path(key_or_url[len("local://") :])
        else:
            p = self._path(key_or_url)
        return p.read_bytes()
