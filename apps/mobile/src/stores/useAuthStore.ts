// 인증 상태 (zustand).
// status:
//   'unknown'        — 부트스트랩 중 (앱 시작 직후, getSession() 결과 대기)
//   'authenticated'  — 유효 세션 있음
//   'unauthenticated'— 세션 없음
import type { Session } from '@supabase/supabase-js';
import { create } from 'zustand';

export type AuthStatus = 'unknown' | 'authenticated' | 'unauthenticated';

interface AuthState {
  status: AuthStatus;
  userId: string | null;
  email: string | null;
  accessToken: string | null;
  setSession: (session: Session | null) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  status: 'unknown',
  userId: null,
  email: null,
  accessToken: null,
  setSession: (session) => {
    if (session?.user) {
      set({
        status: 'authenticated',
        userId: session.user.id,
        email: session.user.email ?? null,
        accessToken: session.access_token,
      });
    } else {
      set({
        status: 'unauthenticated',
        userId: null,
        email: null,
        accessToken: null,
      });
    }
  },
  clear: () =>
    set({
      status: 'unauthenticated',
      userId: null,
      email: null,
      accessToken: null,
    }),
}));
