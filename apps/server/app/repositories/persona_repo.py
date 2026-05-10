from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.persona import Persona
from app.repositories.base import BaseRepository


class PersonaRepository(BaseRepository[Persona]):
    model = Persona

    async def list_for_user(self, user_id: uuid.UUID) -> list[Persona]:
        result = await self.session.execute(
            select(Persona).where(Persona.user_id == user_id).order_by(Persona.created_at.desc()),
        )
        return list(result.scalars().all())
