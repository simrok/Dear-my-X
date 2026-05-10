"""UploadService — 카카오톡 txt → 파싱 → 마스킹 → 청크 → 임베딩 → memory_chunks.

흐름 (controller 가 두 단계로 호출):

    [1] preview_kakao(persona_id, file_bytes, original_filename)
        - LocalStorage 에 원본 저장
        - KakaoParser 로 발화자 + 메타 추출
        - ConversationUpload row 생성 (status='pending')
        - 응답으로 upload_id, speakers 반환

    [2] ingest_kakao(upload_id, speaker)
        - status 'parsing' → 다시 파일 read & parse
        - speaker 의 메시지만 필터링
        - PIIMasker 로 본문 마스킹
        - ConversationChunker 로 chunk 분리
        - status 'embedding' → embedder.embed_many
        - MemoryChunkRepository.bulk_create
        - status 'completed'
        - 실패 시 status 'failed' + error 메시지

도메인 에러는 raise → API 가 401/403/404/422 등으로 매핑.
파이프라인 내부 에러 (parser/embedding) 는 status='failed' 로 기록 후 IngestResponse 반환.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chunkers.conversation_chunker import ConversationChunker
from app.ai.clients.embedding_client import EmbeddingClient, EmbeddingError
from app.ai.masking.pii_masker import PIIMasker
from app.ai.parsers.kakao_parser import KakaoParser
from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.integrations.storage.local import LocalStorage
from app.models.conversation_upload import ConversationUpload
from app.repositories.memory_repo import MemoryChunkRepository
from app.repositories.upload_repo import ConversationUploadRepository
from app.schemas.upload import IngestResponse, KakaoPreviewResponse
from app.services.persona_service import PersonaService

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_FORMATS = {"pc", "mobile"}


@dataclass
class UploadDeps:
    parser: KakaoParser
    masker: PIIMasker
    chunker: ConversationChunker
    embedder: EmbeddingClient
    storage: LocalStorage


class UploadService:
    def __init__(self, session: AsyncSession, ai: UploadDeps) -> None:
        self.session = session
        self.ai = ai
        self.uploads = ConversationUploadRepository(session)
        self.memories = MemoryChunkRepository(session)
        self.personas = PersonaService(session)

    # ----------------------------------------------------------------- preview
    async def preview_kakao(
        self,
        *,
        user_id: uuid.UUID,
        persona_id: uuid.UUID,
        file_bytes: bytes,
        original_filename: str,
    ) -> KakaoPreviewResponse:
        # 1) 입력 검증
        if not file_bytes:
            raise ValidationError("파일이 비어 있어요.")
        if len(file_bytes) > MAX_FILE_BYTES:
            raise ValidationError(
                f"파일이 너무 커요. 최대 {MAX_FILE_BYTES // (1024 * 1024)} MB까지 지원합니다.",
            )
        # 2) 페르소나 소유 검증 (없으면 404 / 403)
        persona = await self.personas.get_owned(user_id=user_id, persona_id=persona_id)

        # 3) 인코딩 디코드 (BOM 포함 UTF-8 우선, 실패 시 cp949)
        try:
            text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                text = file_bytes.decode("cp949")
            except UnicodeDecodeError as exc:
                raise ValidationError(
                    "텍스트 인코딩을 인식하지 못했어요. UTF-8 또는 CP949 파일이 필요합니다.",
                ) from exc

        # 4) 파싱
        result = self.ai.parser.parse(text)
        if not result.messages:
            raise ValidationError(
                "메시지를 한 건도 추출하지 못했어요. 카카오톡 .txt 내보내기 파일이 맞는지 확인해 주세요.",
            )
        if result.detected_format not in ALLOWED_FORMATS:
            raise ValidationError("지원하지 않는 카카오톡 .txt 형식입니다.")

        # 5) 원본 저장 (LocalStorage)
        upload_id = uuid.uuid4()
        key = f"{user_id}/{persona.id}/{upload_id}.txt"
        file_url = await self.ai.storage.upload_bytes(
            key=key, data=file_bytes, content_type="text/plain"
        )

        # 6) DB row
        await self.uploads.create(
            id=upload_id,
            user_id=user_id,
            persona_id=persona.id,
            file_url=file_url,
            original_filename=original_filename[:512],
            status="pending",
        )
        await self.session.commit()

        return KakaoPreviewResponse(
            upload_id=upload_id,
            status="pending",
            speakers=result.speakers,
            detected_format=result.detected_format,
            message_count=len(result.messages),
            skipped_lines=result.skipped_lines,
        )

    # ----------------------------------------------------------------- ingest
    async def ingest_kakao(
        self,
        *,
        user_id: uuid.UUID,
        upload_id: uuid.UUID,
        speaker: str,
    ) -> IngestResponse:
        upload = await self.uploads.get(upload_id)
        if upload is None:
            raise NotFoundError("업로드를 찾을 수 없어요.")
        if upload.user_id != user_id:
            raise ForbiddenError("권한이 없어요.")

        speaker = speaker.strip()
        if not speaker:
            raise ValidationError("발화자를 선택해 주세요.")

        try:
            # parsing
            await self._set_status(upload, "parsing")
            file_bytes = await self.ai.storage.read_bytes(upload.file_url)
            try:
                text = file_bytes.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = file_bytes.decode("cp949", errors="ignore")

            result = self.ai.parser.parse(text)
            if speaker not in result.speakers:
                raise ValidationError(
                    f"파일에 '{speaker}' 발화자가 없어요. 후보: {', '.join(result.speakers)}",
                )
            target_msgs = [m for m in result.messages if m.speaker == speaker]
            if not target_msgs:
                raise ValidationError(f"'{speaker}' 의 메시지를 찾지 못했어요.")

            # masking
            mask_counts: dict[str, int] = {}
            for m in target_msgs:
                masked = self.ai.masker.mask_with_stats(m.text)
                m.text = masked.text
                for k, v in masked.counts.items():
                    mask_counts[k] = mask_counts.get(k, 0) + v

            # chunking
            chunks = self.ai.chunker.chunk_messages(
                target_msgs,
                source=f"kakao:{upload_id}",
            )
            if not chunks:
                raise ValidationError("청크를 만들 텍스트가 부족해요.")

            # embedding
            await self._set_status(upload, "embedding")
            vectors = await self.ai.embedder.embed_many([c.text for c in chunks])
            if len(vectors) != len(chunks):
                raise EmbeddingError("embedding count mismatch")

            # save
            rows = [
                {
                    "user_id": user_id,
                    "persona_id": upload.persona_id,
                    "content": chunks[i].text,
                    "speaker": chunks[i].speaker,
                    "source": chunks[i].source,
                    "embedding": vectors[i],
                }
                for i in range(len(chunks))
            ]
            inserted = await self.memories.bulk_create(rows=rows)
            await self.session.commit()  # bulk_create flush 후 최종 commit

            await self._set_status(upload, "completed")

            return IngestResponse(
                upload_id=upload_id,
                status="completed",
                speaker=speaker,
                chunks_created=inserted,
                masked_counts=mask_counts,
            )

        except (ValidationError, ForbiddenError, NotFoundError):
            await self._set_status(upload, "failed")
            raise
        except Exception as e:
            # 파이프라인 실패: 상태 기록 + 에러 메시지를 응답으로 (라우트는 200 OK + status=failed)
            await self._set_status(upload, "failed")
            return IngestResponse(
                upload_id=upload_id,
                status="failed",
                speaker=speaker,
                chunks_created=0,
                masked_counts={},
                error=str(e),
            )

    # ----------------------------------------------------------------- status
    async def get_upload(
        self, *, user_id: uuid.UUID, upload_id: uuid.UUID
    ) -> ConversationUpload:
        upload = await self.uploads.get(upload_id)
        if upload is None:
            raise NotFoundError("업로드를 찾을 수 없어요.")
        if upload.user_id != user_id:
            raise ForbiddenError("권한이 없어요.")
        return upload

    # 파서 단독 (테스트 / 디버그)
    async def extract_speakers(self, file_bytes: bytes) -> list[str]:
        text = file_bytes.decode("utf-8-sig", errors="ignore")
        return self.ai.parser.extract_speakers(text)

    async def _set_status(self, upload: ConversationUpload, new_status: str) -> None:
        upload.status = new_status
        self.session.add(upload)
        await self.session.commit()
