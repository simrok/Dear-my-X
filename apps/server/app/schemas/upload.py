from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import ORMModel

UploadStatus = Literal["pending", "parsing", "embedding", "completed", "failed"]


class UploadRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    persona_id: uuid.UUID
    file_url: str
    original_filename: str
    status: str
    created_at: datetime


# --- Kakao 전용 ---


class KakaoPreviewResponse(BaseModel):
    upload_id: uuid.UUID
    status: UploadStatus
    speakers: list[str]
    detected_format: str            # "pc" | "mobile" | "unknown"
    message_count: int              # 파싱된 메시지 수
    skipped_lines: int


class IngestRequest(BaseModel):
    speaker: str                    # AI 페르소나로 사용할 발화자 이름


class IngestResponse(BaseModel):
    upload_id: uuid.UUID
    status: UploadStatus
    speaker: str
    chunks_created: int
    masked_counts: dict[str, int]   # {"PHONE": 3, "EMAIL": 1, ...}
    error: str | None = None


class UploadStatusResponse(BaseModel):
    upload_id: uuid.UUID
    status: UploadStatus
    persona_id: uuid.UUID
    original_filename: str
    created_at: datetime
