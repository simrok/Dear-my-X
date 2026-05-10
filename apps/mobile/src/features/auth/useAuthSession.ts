// Supabase 세션 ↔ zustand 스토어 동기화.
// App 루트에서 한 번 호출하면, 이후 인증 상태가 자동으로 스토어에 반영된다.
import { useEffect } from 'react';

import { SupabaseAuth } from '@/services/supabase/auth';
import { useAuthStore } from '@/stores/useAuthStore';

export function useAuthSession(): void {
  const setSession = useAuthStore((s) => s.setSession);

  useEffect(() => {
    let mounted = true;

    // 1) 부트스트랩: 현재 세션 한 번 읽기
    void SupabaseAuth.getSession().then(({ data }) => {
      if (!mounted) return;
      setSession(data.session);
    });

    // 2) 변경 구독 (signIn / signOut / 토큰 갱신)
    const { data: sub } = SupabaseAuth.onAuthStateChange((_event, session) => {
      if (!mounted) return;
      setSession(session);
    });

    return () => {
      mounted = false;
      sub.subscription.unsubscribe();
    };
  }, [setSession]);
}
