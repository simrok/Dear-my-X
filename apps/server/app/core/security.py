"""보안 / 인증 헬퍼.

MVP 인증은 Supabase Auth 가 발급한 JWT 를 검증하는 방식으로 단순화한다.
서버는 사용자 ID(`sub`)와 이메일만 신뢰하면 되며, 비밀번호 자체는 보관하지 않는다.
"""

from __future__ import annotations

from typing import Any

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedError


def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """Supabase JWT 검증.

    Supabase 는 HS256 으로 JWT 를 발급한다 (서비스 키는 다른 비밀).
    검증 실패 시 `UnauthorizedError` 발생.
    """
    if not settings.SUPABASE_JWT_SECRET:
        # 서버 설정 누락은 인증 실패가 아닌 서버 오류지만, 외부에는 401 로 보낸다.
        raise UnauthorizedError("Server is not configured for authentication")
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    return payload
