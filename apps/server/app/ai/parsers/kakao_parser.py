"""카카오톡 .txt 대화 파서.

지원 포맷:
    1. PC (Windows / macOS) 내보내기 — 1순위 지원
    2. 모바일 (Android / iOS) 내보내기 — best-effort

제한 사항:
    - 한국어 ko_KR 가정 (다른 로케일 미지원)
    - 사진 / 동영상 / 이모티콘 / 파일 등 미디어 라인은 본문에서 제외
    - 멀티라인 메시지는 다음 형식 라인이 나올 때까지 이어 붙임
    - 시스템 메시지는 무시
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time


# --- regex ---
RE_DATE_SEPARATOR_PC = re.compile(
    r"^-+\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일.*-+\s*$"
)
RE_MESSAGE_PC = re.compile(
    r"^\[(?P<speaker>.+?)\]\s*\[(?P<ampm>오전|오후)\s*(?P<hour>\d{1,2}):(?P<minute>\d{2})\]\s*(?P<text>.*)$"
)
RE_MESSAGE_MOBILE = re.compile(
    r"^(?P<year>\d{4})[년.\s]+(?P<month>\d{1,2})[월.\s]+(?P<day>\d{1,2})[일.\s]+"
    r"(?P<ampm>오전|오후)\s*(?P<hour>\d{1,2}):(?P<minute>\d{2}),\s*(?P<speaker>[^:]+?)\s*:\s*(?P<text>.*)$"
)
RE_SYSTEM = re.compile(
    r"(님이 들어왔습니다\.|님이 나갔습니다\.|님을 초대했습니다\.|"
    r"님이 .* 내보냈습니다\.|채팅방을 만들었습니다\.|"
    r"^저장한 날짜\s*[:：]|^.+ 님과 카톡대화|^.+ 님과의 카카오톡 대화)"
)
RE_MEDIA_ONLY = re.compile(r"^(사진|사진 \d+장|동영상|이모티콘|음성메시지|파일|<.+>)\s*$")


@dataclass
class KakaoMessage:
    speaker: str
    timestamp: datetime | None
    text: str


@dataclass
class ParseResult:
    messages: list[KakaoMessage] = field(default_factory=list)
    speakers: list[str] = field(default_factory=list)
    detected_format: str = "unknown"
    skipped_lines: int = 0


def _to_24h(ampm: str, hour: int, minute: int) -> time:
    h = hour % 12
    if ampm == "오후":
        h += 12
    return time(hour=h, minute=minute)


class KakaoParser:
    def parse(self, raw_text: str) -> ParseResult:
        result = ParseResult()
        if raw_text.startswith("﻿"):
            raw_text = raw_text[1:]

        current_date: date | None = None
        last_msg: KakaoMessage | None = None
        seen_speakers: dict[str, None] = {}
        format_votes = {"pc": 0, "mobile": 0}

        for raw_line in raw_text.splitlines():
            line = raw_line.rstrip()

            if not line:
                last_msg = None
                continue

            if RE_SYSTEM.search(line):
                result.skipped_lines += 1
                last_msg = None
                continue

            m = RE_DATE_SEPARATOR_PC.match(line)
            if m:
                current_date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                last_msg = None
                continue

            # **미디어 only 라인 먼저 체크** — PC/모바일 형식보다 앞에 두어
            # 멀티라인 흡수 / 본문 매칭 모두로 빠지지 않게.
            stripped = line.strip()
            if RE_MEDIA_ONLY.match(stripped):
                result.skipped_lines += 1
                last_msg = None
                continue

            m = RE_MESSAGE_PC.match(line)
            if m:
                format_votes["pc"] += 1
                speaker = m.group("speaker").strip()
                t = _to_24h(m.group("ampm"), int(m.group("hour")), int(m.group("minute")))
                ts = datetime.combine(current_date, t) if current_date else None
                text = m.group("text").strip()
                if not text or RE_MEDIA_ONLY.match(text):
                    result.skipped_lines += 1
                    last_msg = None
                    continue
                msg = KakaoMessage(speaker=speaker, timestamp=ts, text=text)
                result.messages.append(msg)
                seen_speakers.setdefault(speaker, None)
                last_msg = msg
                continue

            m = RE_MESSAGE_MOBILE.match(line)
            if m:
                format_votes["mobile"] += 1
                speaker = m.group("speaker").strip()
                d = date(int(m.group("year")), int(m.group("month")), int(m.group("day")))
                t = _to_24h(m.group("ampm"), int(m.group("hour")), int(m.group("minute")))
                ts = datetime.combine(d, t)
                text = m.group("text").strip()
                if not text or RE_MEDIA_ONLY.match(text):
                    result.skipped_lines += 1
                    last_msg = None
                    continue
                msg = KakaoMessage(speaker=speaker, timestamp=ts, text=text)
                result.messages.append(msg)
                seen_speakers.setdefault(speaker, None)
                last_msg = msg
                continue

            # 어디에도 매칭 안 된 줄: 직전 메시지의 멀티라인 본문으로 흡수
            if last_msg is not None:
                last_msg.text = (last_msg.text + "\n" + line).strip()
            else:
                result.skipped_lines += 1

        result.speakers = list(seen_speakers.keys())
        result.detected_format = (
            "pc"
            if format_votes["pc"] >= format_votes["mobile"] and format_votes["pc"] > 0
            else ("mobile" if format_votes["mobile"] > 0 else "unknown")
        )
        return result

    def extract_speakers(self, raw_text: str) -> list[str]:
        return self.parse(raw_text).speakers

    def extract_for_speaker(self, raw_text: str, speaker: str) -> list[KakaoMessage]:
        return [m for m in self.parse(raw_text).messages if m.speaker == speaker]
