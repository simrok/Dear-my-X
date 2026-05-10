"""FastAPI 공통 의존성.

- `get_db` (DB 세션)
- `get_current_user` (Supabase JWT 검증)
- AI 어댑터 / 서비스 팩토리

서비스는 라우트에서 `Depends(...)` 로 주입받아 사용한다.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.chunkers.conversation_chunker import ConversationChunker
from app.ai.clients.claude_client import ClaudeClient
from app.ai.clients.embedding_client import OpenAIEmbeddingClient
from app.ai.masking.pii_masker import PIIMasker
from app.ai.parsers.kakao_parser import KakaoParser
from app.ai.rag.retriever import MemoryRetriever
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_supabase_jwt
from app.db.session import get_db as _get_db
from app.integrations.storage.local import LocalStorage
from app.repositories.memory_repo import MemoryChunkRepository
from app.services.auth_service import AuthService
from app.services.chat_service import ChatDeps, ChatService
from app.services.persona_service import PersonaService
from app.services.upload_service import UploadDeps, UploadService


# --- DB ---
async def get_db() -> AsyncIterator[AsyncSession]:
    async for session in _get_db():
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]


# --- 현재 사용자 ---
class CurrentUser:
    def __init__(self, id: uuid.UUID, email: str | None) -> None:
        self.id = id
        self.email = email


async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token")
    token = authorization.split(" ", 1)[1]
    payload = decode_supabase_jwt(token)
    sub = payload.get("sub")
    if not sub:
        raise UnauthorizedError("Token missing sub")
    return CurrentUser(id=uuid.UUID(sub), email=payload.get("email"))


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


# --- AI 어댑터 ---
def get_claude_client() -> ClaudeClient:
    return ClaudeClient()


def get_embedding_client() -> OpenAIEmbeddingClient:
    return OpenAIEmbeddingClient()


_storage_singleton: LocalStorage | None = None


def get_storage() -> LocalStorage:
    """업로드 원본 저장. MVP=LocalStorage. 추후 SupabaseStorage 로 교체."""
    global _storage_singleton
    if _storage_singleton is None:
        _storage_singleton = LocalStorage()
    return _storage_singleton


# --- 서비스 팩토리 ---
def get_auth_service(session: DbSession) -> AuthService:
    return AuthService(session)


def get_persona_service(session: DbSession) -> PersonaService:
    return PersonaService(session)


def get_chat_service(
    session: DbSession,
    claude: Annotated[ClaudeClient, Depends(get_claude_client)],
    embedder: Annotated[OpenAIEmbeddingClient, Depends(get_embedding_client)],
) -> ChatService:
    retriever = MemoryRetriever(embedder=embedder, repo=MemoryChunkRepository(session))
    return ChatService(
        session,
        ai=ChatDeps(claude=claude, embedder=embedder, retriever=retriever),
    )


def get_upload_service(
    session: DbSession,
    embedder: Annotated[OpenAIEmbeddingClient, Depends(get_embedding_client)],
    storage: Annotated[LocalStorage, Depends(get_storage)],
) -> UploadService:
    return UploadService(
        session,
        ai=UploadDeps(
            parser=KakaoParser(),
            masker=PIIMasker(),
            chunker=ConversationChunker(),
            embedder=embedder,
            storage=storage,
        ),
    )
