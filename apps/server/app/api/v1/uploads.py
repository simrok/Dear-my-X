"""업로드 라우트 (controller).

흐름:
    POST /uploads/kakao                    multipart (file + persona_id)
        → preview: 발화자 추출 + ConversationUpload(pending) 생성
    POST /uploads/kakao/{upload_id}/ingest body { speaker }
        → mask → chunk → embed → memory_chunks 저장
    GET  /uploads/kakao/{upload_id}        현재 상태 조회
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import CurrentUserDep, get_upload_service
from app.schemas.upload import (
    IngestRequest,
    IngestResponse,
    KakaoPreviewResponse,
    UploadStatusResponse,
)
from app.services.upload_service import UploadService

router = APIRouter()
UploadServiceDep = Annotated[UploadService, Depends(get_upload_service)]


@router.post("/kakao", response_model=KakaoPreviewResponse, status_code=201)
async def upload_kakao(
    user: CurrentUserDep,
    service: UploadServiceDep,
    file: Annotated[UploadFile, File(description="카카오톡 .txt 내보내기 파일")],
    persona_id: Annotated[uuid.UUID, Form()],
) -> KakaoPreviewResponse:
    """카카오톡 .txt 업로드 → 발화자/메타 미리보기 반환."""
    contents = await file.read()
    return await service.preview_kakao(
        user_id=user.id,
        persona_id=persona_id,
        file_bytes=contents,
        original_filename=file.filename or "kakao.txt",
    )


@router.post("/kakao/{upload_id}/ingest", response_model=IngestResponse)
async def ingest_kakao(
    upload_id: uuid.UUID,
    body: IngestRequest,
    user: CurrentUserDep,
    service: UploadServiceDep,
) -> IngestResponse:
    """선택된 발화자 기준으로 마스킹 → 청크 → 임베딩 → memory_chunks 저장."""
    return await service.ingest_kakao(
        user_id=user.id, upload_id=upload_id, speaker=body.speaker
    )


@router.get("/kakao/{upload_id}", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: uuid.UUID,
    user: CurrentUserDep,
    service: UploadServiceDep,
) -> UploadStatusResponse:
    upload = await service.get_upload(user_id=user.id, upload_id=upload_id)
    return UploadStatusResponse(
        upload_id=upload.id,
        status=upload.status,  # type: ignore[arg-type]
        persona_id=upload.persona_id,
        original_filename=upload.original_filename,
        created_at=upload.created_at,
    )
