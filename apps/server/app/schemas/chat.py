from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ChatRoomRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    persona_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageRead(ORMModel):
    id: uuid.UUID
    chat_room_id: uuid.UUID
    sender_type: str
    content: str
    created_at: datetime
