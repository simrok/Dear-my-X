"""AuthService.

Supabase Auth 가 권위 있는 인증 제공자. 우리 DB(`users` 테이블)는
Supabase 의 user UUID 를 그대로 PK 로 갖는 미러일 뿐이다.

이 서비스는 "현재 JWT 가 가리키는 사용자가 우리 DB 에도 존재함을 보장"하는
역할만 한다. 사용자 신규 가입 / 첫 로그인 시 자동으로 한 행을 만든다.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def ensure_user(self, *, user_id: uuid.UUID, email: str | None) -> User:
        """JWT 의 sub/email 로 users 테이블을 보장한다.

        email 이 비어 있으면 인증 실패로 간주 (MVP 정책).
        """
        if not email:
            raise UnauthorizedError("Token does not contain an email claim")

        user, created = await self.users.get_or_create(user_id=user_id, email=email)
        if created:
            await self.session.commit()
        return user
