from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.conversation_upload import ConversationUpload
from app.repositories.base import BaseRepository


class ConversationUploadRepository(BaseRepository[ConversationUpload]):
    model = ConversationUpload

    async def list_for_persona(
        self, *, user_id: uuid.UUID, persona_id: uuid.UUID
    ) -> list[ConversationUpload]:
        stmt = (
            select(ConversationUpload)
            .where(
                ConversationUpload.user_id == user_id,
                ConversationUpload.persona_id == persona_id,
            )
            .order_by(ConversationUpload.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
