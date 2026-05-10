"""페르소나 system prompt 빌더.

PRD 섹션 5 의 응답 규칙을 코드화. 페르소나 메타데이터 + 검색된 memory chunk 를
합쳐 system prompt 를 만든다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PersonaContext:
    name: str
    relation_type: str
    personality: str | None
    speaking_style: str | None
    safety_notes: str | None


BASE_RULES = """\
너는 사용자가 만든 가상 AI 페르소나다.
실제 인물을 완전히 복제하거나 사칭하지 않는다.

응답 규칙:
- 모바일 채팅처럼 짧게 답한다.
- 너무 설명하지 않는다.
- 감정에 먼저 반응한다.
- 과거 대화 기록에서 확인 가능한 내용만 기억처럼 말한다.
- 모르는 사실은 지어내지 않는다.
- 사용자가 현실 인물이라고 착각하지 않도록 필요 시 부드럽게 경계한다.
- 자해, 집착, 의존적 대화가 감지되면 안전한 방향으로 유도한다.
"""


def build_system_prompt(
    persona: PersonaContext,
    memory_snippets: list[str],
) -> str:
    parts: list[str] = [BASE_RULES, ""]
    parts.append("# 페르소나 설정")
    parts.append(f"이름: {persona.name}")
    parts.append(f"관계: {persona.relation_type}")
    if persona.personality:
        parts.append(f"성격: {persona.personality}")
    if persona.speaking_style:
        parts.append(f"말투: {persona.speaking_style}")
    if persona.safety_notes:
        parts.append(f"주의 주제: {persona.safety_notes}")

    if memory_snippets:
        parts.append("")
        parts.append("# 참고 가능한 과거 대화 단편 (이외의 사실은 지어내지 말 것)")
        for i, snippet in enumerate(memory_snippets, 1):
            parts.append(f"[{i}] {snippet}")

    return "\n".join(parts)
