from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        *,
        user_id: uuid.UUID,
        email: str,
    ) -> tuple[User, bool]:
        """Supabase 가 발급한 user_id 로 조회 후 없으면 생성.

        Returns:
            (user, created) — created=True 면 새로 만들어진 사용자.
        """
        user = await self.session.get(User, user_id)
        if user is not None:
            return user, False

        user = User(id=user_id, email=email)
        self.session.add(user)
        try:
            await self.session.flush()
        except IntegrityError:
            # 동시성: 다른 요청이 먼저 만든 케이스. 다시 조회.
            await self.session.rollback()
            user = await self.session.get(User, user_id)
            if user is None:  # pragma: no cover  (정말 비정상)
                raise
            return user, False
        return user, True
