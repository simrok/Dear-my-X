// Supabase JS 클라이언트.
//
// 안정성:
//   - env 가 비어있으면 createClient(...) 가 throw 하므로 dev 환경에서 앱이 즉시 죽음.
//     placeholder URL 로 fallback 해 부팅은 되게 하고, 실제 호출 시에만 401 등을 받게 한다.
//   - RN 환경에서 세션 영구화는 AsyncStorage 사용. Web 에서는 기본 localStorage.
import { createClient, type SupportedStorage } from '@supabase/supabase-js';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

import { Config } from '@/constants/config';

const PLACEHOLDER_URL = 'https://placeholder.supabase.co';
const PLACEHOLDER_KEY = 'placeholder-anon-key';

const url = Config.supabaseUrl || PLACEHOLDER_URL;
const anonKey = Config.supabaseAnonKey || PLACEHOLDER_KEY;

if (!Config.supabaseUrl || !Config.supabaseAnonKey) {
  // 개발자에게 한 번만 알림. 앱 종료시키지 않음.
  // eslint-disable-next-line no-console
  console.warn(
    '[Supabase] EXPO_PUBLIC_SUPABASE_URL / EXPO_PUBLIC_SUPABASE_ANON_KEY 가 설정되지 않았어요. ' +
      '인증 호출은 실패합니다. apps/mobile/.env 를 확인해 주세요.',
  );
}

const storage: SupportedStorage | undefined =
  Platform.OS === 'web' ? undefined : (AsyncStorage as unknown as SupportedStorage);

export const supabase = createClient(url, anonKey, {
  auth: {
    storage,
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: false,
  },
});
