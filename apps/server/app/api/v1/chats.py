"""채팅방 라우트."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_chat_rooms() -> list[dict[str, str]]:
    """사용자의 채팅방 목록. (스켈레톤)"""
    return []
