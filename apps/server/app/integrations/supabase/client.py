"""Supabase 클라이언트 팩토리."""

from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache(maxsize=1)
def get_supabase_admin() -> Client:
    """서비스 롤 키 사용 (서버 측 전용). RLS 우회 가능."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@lru_cache(maxsize=1)
def get_supabase_anon() -> Client:
    """anon 키 사용 (사용자 토큰을 함께 보낼 때)."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
