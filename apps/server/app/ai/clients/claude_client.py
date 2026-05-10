"""Anthropic Claude 어댑터.

비즈니스 로직은 이 클래스의 메서드만 호출한다.
SDK 시그니처가 바뀌어도 이 파일만 고치면 된다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.core.config import settings


@dataclass
class ChatMessage:
    role: Literal["user", "assistant"]
    content: str


class ClaudeClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL
        # TODO: anthropic.AsyncAnthropic(api_key=self.api_key) 인스턴스 보관
        self._client = None

    async def complete(
        self,
        *,
        system_prompt: str,
        history: list[ChatMessage],
        user_message: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """페르소나 응답 생성. (스켈레톤)"""
        # TODO: anthropic SDK 호출 후 응답 텍스트 반환
        raise NotImplementedError("ClaudeClient.complete 구현 예정")
