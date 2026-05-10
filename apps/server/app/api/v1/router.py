"""v1 라우터 묶음."""

from fastapi import APIRouter

from app.api.v1 import auth, chats, messages, personas, uploads

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
