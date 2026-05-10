"""ConversationChunker — 임베딩 단위로 대화를 chunk 분리.

전략 (MVP):
    1. **연속 같은 발화자** 의 메시지는 하나로 먼저 합친다 (line-join).
    2. 합쳐진 라인을 시간 순으로 이어붙이며, **target_chars** 를 넘기면 끊는다.
    3. chunk 사이에 **overlap_chars** 만큼의 마지막 컨텍스트를 다음 chunk 의 앞에 둔다.
    4. 각 chunk 는 첫 라인의 발화자 / 시간을 메타데이터로 갖는다.

text-embedding-3-small 의 max input 은 8192 토큰 (~ 30000자) 이므로 1500자 내외는 안전.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.ai.parsers.kakao_parser import KakaoMessage


@dataclass
class Chunk:
    text: str                         # 임베딩 대상 본문 (발화자 prefix 포함)
    speaker: str | None = None        # 대표 발화자 (대부분 단일 발화자 chunk)
    started_at: datetime | None = None
    source: str | None = None         # 예: "kakao:upload_id"


def _format_line(msg: KakaoMessage) -> str:
    if msg.timestamp:
        return f"[{msg.timestamp.strftime('%Y-%m-%d %H:%M')}] {msg.speaker}: {msg.text}"
    return f"{msg.speaker}: {msg.text}"


class ConversationChunker:
    def __init__(
        self,
        *,
        target_chars: int = 1200,
        overlap_chars: int = 200,
        min_chunk_chars: int = 80,
    ) -> None:
        if target_chars <= 0:
            raise ValueError("target_chars must be > 0")
        if overlap_chars < 0 or overlap_chars >= target_chars:
            raise ValueError("0 <= overlap_chars < target_chars")
        self.target_chars = target_chars
        self.overlap_chars = overlap_chars
        self.min_chunk_chars = min_chunk_chars

    def chunk_messages(
        self,
        messages: list[KakaoMessage],
        *,
        source: str | None = None,
    ) -> list[Chunk]:
        """KakaoMessage 리스트 → Chunk 리스트.

        messages 는 시간 순서로 정렬되어 있다고 가정.
        """
        if not messages:
            return []

        lines = [_format_line(m) for m in messages]
        chunks: list[Chunk] = []

        buf: list[str] = []
        buf_len = 0
        first_msg_idx = 0  # 현재 buf 가 시작된 messages index

        i = 0
        while i < len(lines):
            line = lines[i]
            line_len = len(line) + 1  # +1 for join newline

            # buf 가 비어 있으면 무조건 추가
            if not buf:
                buf.append(line)
                buf_len = len(line)
                first_msg_idx = i
                i += 1
                continue

            # 추가하면 target 초과 → 현재 buf 를 flush 하고 overlap 으로 새 buf 시작
            if buf_len + line_len > self.target_chars:
                chunks.append(self._make_chunk(buf, messages[first_msg_idx], source))
                # overlap: 직전 buf 의 마지막 N 자를 가져옴
                tail = "\n".join(buf)
                tail = tail[-self.overlap_chars :] if self.overlap_chars else ""
                # 다음 buf 시작점 추정 (overlap 부분의 시작 라인)
                # 정확히 line 단위로 자르지는 않고, 텍스트만 prefix 로 넣음.
                if tail:
                    buf = [tail.lstrip(), line]
                    buf_len = len(tail) + 1 + len(line)
                else:
                    buf = [line]
                    buf_len = len(line)
                first_msg_idx = i
                i += 1
                continue

            # 일반 케이스
            buf.append(line)
            buf_len += line_len
            i += 1

        # 마지막 buf flush
        if buf:
            text = "\n".join(buf).strip()
            if len(text) >= self.min_chunk_chars or not chunks:
                chunks.append(self._make_chunk(buf, messages[first_msg_idx], source))
            else:
                # 너무 짧으면 직전 chunk 에 합침
                prev = chunks[-1]
                merged = (prev.text + "\n" + text).strip()
                chunks[-1] = Chunk(
                    text=merged,
                    speaker=prev.speaker,
                    started_at=prev.started_at,
                    source=prev.source,
                )

        return chunks

    @staticmethod
    def _make_chunk(buf: list[str], first_msg: KakaoMessage, source: str | None) -> Chunk:
        return Chunk(
            text="\n".join(buf).strip(),
            speaker=first_msg.speaker,
            started_at=first_msg.timestamp,
            source=source,
        )
