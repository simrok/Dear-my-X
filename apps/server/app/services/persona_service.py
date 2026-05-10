"""PersonaService — 페르소나 생성/조회/수정."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.persona import Persona
from app.repositories.persona_repo import PersonaRepository
from app.schemas.persona import PersonaCreate, PersonaUpdate


class PersonaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = PersonaRepository(session)

    async def create(self, *, user_id: uuid.UUID, data: PersonaCreate) -> Persona:
        if not (data.consent_virtual_persona and data.consent_data_rights):
            raise ValidationError("필수 동의 항목이 체크되지 않았습니다.")
        persona = await self.repo.create(
            user_id=user_id,
            name=data.name,
            relation_type=data.relation_type,
            personality=data.personality,
            speaking_style=data.speaking_style,
            profile_image_url=data.profile_image_url,
            safety_notes=data.safety_notes,
        )
        await self.session.commit()
        return persona

    async def list_mine(self, *, user_id: uuid.UUID) -> list[Persona]:
        return await self.repo.list_for_user(user_id)

    async def get_owned(self, *, user_id: uuid.UUID, persona_id: uuid.UUID) -> Persona:
        persona = await self.repo.get(persona_id)
        if persona is None:
            raise NotFoundError("페르소나를 찾을 수 없습니다.")
        if persona.user_id != user_id:
            raise ForbiddenError("권한이 없습니다.")
        return persona

    async def update(
        self,
        *,
        user_id: uuid.UUID,
        persona_id: uuid.UUID,
        data: PersonaUpdate,
    ) -> Persona:
        persona = await self.get_owned(user_id=user_id, persona_id=persona_id)
        updates = data.model_dump(exclude_unset=True)
        await self.repo.update(persona, **updates)
        await self.session.commit()
        return persona

    async def delete(self, *, user_id: uuid.UUID, persona_id: uuid.UUID) -> None:
        # 소유 검증을 먼저 수행 (없으면 NotFound, 남이면 Forbidden).
        persona = await self.get_owned(user_id=user_id, persona_id=persona_id)
        await self.session.delete(persona)
        await self.session.commit()
