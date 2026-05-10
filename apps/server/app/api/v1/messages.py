"""메시지 송수신 라우트."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserDep, get_chat_service
from app.schemas.chat import MessageCreate, MessageRead
from app.services.chat_service import ChatService

router = APIRouter()

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]


@router.post("/{chat_room_id}", response_model=MessageRead)
async def send_message(
    chat_room_id: uuid.UUID,
    body: MessageCreate,
    user: CurrentUserDep,
    service: ChatServiceDep,
) -> MessageRead:
    msg = await service.send_message(
        user_id=user.id,
        chat_room_id=chat_room_id,
        content=body.content,
    )
    return MessageRead.model_validate(msg)
