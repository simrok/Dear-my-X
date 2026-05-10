// 세션 헬퍼.
// 1순위: zustand 스토어에 캐시된 access_token (싱크론)
// 폴백: supabase.auth.getSession() — 비동기, 부트스트랩 직후 등에 필요
import { useAuthStore } from '@/stores/useAuthStore';

import { supabase } from './client';

export async function getAccessToken(): Promise<string | null> {
  const cached = useAuthStore.getState().accessToken;
  if (cached) return cached;

  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}
