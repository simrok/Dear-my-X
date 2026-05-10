"""Auth 라우트.

Supabase Auth 가 권위 있는 인증을 담당. 서버는 발급된 JWT 를 검증해서
"현재 사용자" 정보를 알려주고, 우리 DB(`users`) 와도 동기화한다.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserDep, get_auth_service
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.get("/me", response_model=UserRead)
async def me(user: CurrentUserDep, service: AuthServiceDep) -> UserRead:
    """JWT 가 가리키는 사용자를 반환. 첫 호출이면 우리 DB 에 사용자 행을 만든다.

    응답:
        200 OK  → UserRead
        401     → JWT 누락 / 만료 / 부정 / email claim 누락 (서버 측 정책)
    """
    db_user = await service.ensure_user(user_id=user.id, email=user.email)
    return UserRead.model_validate(db_user)
