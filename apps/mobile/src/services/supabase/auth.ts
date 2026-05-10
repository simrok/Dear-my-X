// Supabase Auth 의 얇은 래퍼.
// 비즈니스 로직(에러 메시지 매핑 등)은 features/auth 에서 처리.
import type { AuthChangeEvent, Session } from '@supabase/supabase-js';

import { supabase } from './client';

export const SupabaseAuth = {
  signInWithEmail: (email: string, password: string) =>
    supabase.auth.signInWithPassword({ email, password }),

  signUpWithEmail: (email: string, password: string) =>
    supabase.auth.signUp({ email, password }),

  signOut: () => supabase.auth.signOut(),

  getSession: () => supabase.auth.getSession(),

  onAuthStateChange: (cb: (event: AuthChangeEvent, session: Session | null) => void) =>
    supabase.auth.onAuthStateChange(cb),
};
