from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.chat_room import ChatRoom
from app.models.message import Message
from app.repositories.base import BaseRepository


class ChatRoomRepository(BaseRepository[ChatRoom]):
    model = ChatRoom

    async def list_for_user(self, user_id: uuid.UUID) -> list[ChatRoom]:
        result = await self.session.execute(
            select(ChatRoom)
            .where(ChatRoom.user_id == user_id)
            .order_by(ChatRoom.updated_at.desc()),
        )
        return list(result.scalars().all())


class MessageRepository(BaseRepository[Message]):
    model = Message

    async def list_recent(self, chat_room_id: uuid.UUID, limit: int = 20) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_room_id == chat_room_id)
            .order_by(Message.created_at.desc())
            .limit(limit),
        )
        return list(reversed(list(result.scalars().all())))
