// 환경 변수 → 타입드 설정.
// Expo: EXPO_PUBLIC_ 접두어 변수만 process.env 에서 접근 가능.

export const Config = {
  apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://localhost:8000',
  apiVersion: process.env.EXPO_PUBLIC_API_VERSION ?? 'v1',
  supabaseUrl: process.env.EXPO_PUBLIC_SUPABASE_URL ?? '',
  supabaseAnonKey: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '',
  appEnv: (process.env.EXPO_PUBLIC_APP_ENV ?? 'development') as
    | 'development'
    | 'staging'
    | 'production',
} as const;

export const apiUrl = (path: string): string =>
  `${Config.apiBaseUrl}/api/${Config.apiVersion}${path.startsWith('/') ? path : `/${path}`}`;
