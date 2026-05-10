"""ChatService — 채팅 주 흐름.

흐름 (services 가 ai/ 를 어떻게 조립해서 쓰는지의 청사진):
    1. 사용자 메시지 저장
    2. ai.rag.retriever 로 관련 memory chunk 검색
    3. ai.prompts.persona_prompt 로 system prompt 구성
    4. ai.clients.claude_client 로 응답 생성
    5. AI 메시지 저장 후 반환

실제 구현은 추후 단계에서 채워 넣는다 (지금은 스캐폴딩만).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.clients.claude_client import ClaudeClient
from app.ai.clients.embedding_client import EmbeddingClient
from app.ai.rag.retriever import MemoryRetriever
from app.models.message import Message
from app.repositories.chat_repo import ChatRoomRepository, MessageRepository


@dataclass
class ChatDeps:
    """ChatService 가 필요로 하는 AI 의존성 묶음."""

    claude: ClaudeClient
    embedder: EmbeddingClient
    retriever: MemoryRetriever


class ChatService:
    def __init__(self, session: AsyncSession, ai: ChatDeps) -> None:
        self.session = session
        self.ai = ai
        self.rooms = ChatRoomRepository(session)
        self.messages = MessageRepository(session)

    async def send_message(
        self,
        *,
        user_id: uuid.UUID,
        chat_room_id: uuid.UUID,
        content: str,
    ) -> Message:
        """사용자 메시지 처리 + AI 응답 생성. (스켈레톤)"""
        # TODO:
        # 1) chat_room 소유 확인
        # 2) user 메시지 저장
        # 3) embedder.embed(content) -> retriever.search(...) 로 memory chunk
        # 4) recent messages 20개 조회
        # 5) claude.complete(system_prompt, history, user_msg) -> 응답
        # 6) AI 메시지 저장
        raise NotImplementedError("ChatService.send_message 구현 예정")
