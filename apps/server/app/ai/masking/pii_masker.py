"""PII (개인정보) 마스킹.

원칙:
    - **삭제하지 않고 토큰으로 치환** ([PHONE], [EMAIL] 등). 의미 단위는 보존되어
      LLM 이 "여기에 전화번호가 있었다" 정도는 알게 함.
    - **순서가 중요**: 더 구체적인 패턴 (RRN, phone, account) 을 일반적인 숫자
      패턴 (account 등) 보다 먼저 적용해서 잘못 매칭되지 않게 함.
    - **regex 기반 MVP**. 추후 NER 모델 (e.g. spaCy + 한국어) 로 교체 가능하도록
      `mask` 메서드만 안정화.

대응 패턴 (순서대로 치환):
    1. 주민등록번호       → [RRN]
    2. URL               → [URL]
    3. 이메일             → [EMAIL]
    4. 전화번호 (휴대폰)  → [PHONE]
    5. 일반 전화 (지역)   → [PHONE]
    6. 카드번호 (4-4-4-4) → [CARD]
    7. 계좌번호 (3-3+ 숫자블록) → [ACCOUNT]
    8. 주소 휴리스틱      → [ADDRESS]
    9. 실명 후보 (XX씨/님) → [NAME]   (약한 휴리스틱)
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class _Pattern:
    name: str
    regex: re.Pattern[str]


# 1) 주민등록번호: 6자리-1~4로 시작하는 7자리
RE_RRN = re.compile(r"\b\d{6}-[1-4]\d{6}\b")

# 2) URL: http(s)://, 도메인.kr/com 등
RE_URL = re.compile(r"https?://[^\s)>\]]+")

# 3) 이메일
RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# 4) 휴대폰: 양옆이 숫자가 아닐 때만 (한글 인접 OK)
RE_PHONE_MOBILE = re.compile(r"(?<![0-9])01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}(?![0-9])")

# 5) 일반전화: 02-XXX-XXXX, 0XX-XXX-XXXX
RE_PHONE_LANDLINE = re.compile(r"(?<![0-9])0(?:2|[3-9]\d)[-.\s]?\d{3,4}[-.\s]?\d{4}(?![0-9])")

# 6) 카드번호: 4-4-4-4
RE_CARD = re.compile(r"\b\d{4}[-.\s]\d{4}[-.\s]\d{4}[-.\s]\d{4}\b")

# 7) 계좌번호: 3개 이상 숫자 블록을 - 으로 연결 (10~16자리)
RE_ACCOUNT = re.compile(r"\b\d{2,6}-\d{2,6}-\d{2,6}(?:-\d{1,6})?\b")

# 8) 주소 휴리스틱: "XX동/로/길 + 숫자(번지/호)"
RE_ADDRESS = re.compile(
    r"(?:[가-힣]{2,15}(?:동|로|길|읍|면|리))\s*\d{1,5}(?:[-]\d{1,5})?(?:번지|호)?"
)

# 9) 실명 후보 (약한 휴리스틱): 호칭 뒤
RE_NAME_HONORIFIC = re.compile(r"(?<![가-힣])[가-힣]{2,4}(?=\s?(?:사장님|선생님|씨|님)\b)")

_PATTERNS: list[_Pattern] = [
    _Pattern("RRN", RE_RRN),
    _Pattern("URL", RE_URL),
    _Pattern("EMAIL", RE_EMAIL),
    _Pattern("PHONE", RE_PHONE_MOBILE),
    _Pattern("PHONE", RE_PHONE_LANDLINE),
    _Pattern("CARD", RE_CARD),
    _Pattern("ACCOUNT", RE_ACCOUNT),
    _Pattern("ADDRESS", RE_ADDRESS),
    _Pattern("NAME", RE_NAME_HONORIFIC),
]


@dataclass
class MaskResult:
    text: str
    counts: dict[str, int]


class PIIMasker:
    """텍스트 내 PII 를 안전한 토큰으로 치환."""

    def mask(self, text: str) -> str:
        return self.mask_with_stats(text).text

    def mask_with_stats(self, text: str) -> MaskResult:
        counts: dict[str, int] = {}
        out = text
        for p in _PATTERNS:
            new_out, n = p.regex.subn(f"[{p.name}]", out)
            if n > 0:
                counts[p.name] = counts.get(p.name, 0) + n
            out = new_out
        return MaskResult(text=out, counts=counts)

    def mask_many(self, texts: list[str]) -> list[str]:
        return [self.mask(t) for t in texts]
