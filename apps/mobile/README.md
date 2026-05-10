# Dear my X — Mobile (Expo + React Native)

가상 AI 페르소나 채팅 앱의 모바일 클라이언트.

## 폴더 구조

```
apps/mobile/
├── App.tsx
├── app.json
├── babel.config.js
├── metro.config.js
├── tsconfig.json
├── package.json
├── .env.example
├── assets/
└── src/
    ├── app/                  # 앱 루트 (Provider, Navigator)
    ├── navigation/           # React Navigation 라우트 정의
    ├── screens/              # 화면 단위 컴포넌트
    │   ├── onboarding/
    │   ├── auth/
    │   ├── home/
    │   ├── persona/
    │   ├── upload/
    │   ├── chat/
    │   └── settings/
    ├── components/
    │   ├── ui/               # 디자인 시스템 atoms
    │   └── common/
    ├── features/             # 기능 모듈 (auth, persona, chat, upload)
    ├── services/
    │   ├── api/              # 서버 REST 클라이언트
    │   ├── supabase/         # Supabase JS 클라이언트
    │   └── storage/          # SecureStore wrapper 등
    ├── stores/               # 전역 상태 (zustand)
    ├── hooks/
    ├── theme/                # 색상, 타이포, 간격 등 디자인 토큰
    ├── utils/
    ├── constants/
    └── types/
```

## 실행

```bash
# 루트에서 의존성 설치
pnpm install

# 환경변수
cp apps/mobile/.env.example apps/mobile/.env

# 개발 서버
pnpm mobile:start
# 또는
cd apps/mobile && pnpm start
```

## 모바일 우선 + 웹 가능성

- 모든 디자인은 모바일 화면을 기준으로 작성합니다.
- 비즈니스 로직 / API 클라이언트는 `services/`, 도메인 타입은 `@dear-my-x/shared` 에서 가져옵니다.
- 추후 `apps/web` (Next.js 등) 추가 시 `services/` 의 일부와 `@dear-my-x/shared` 를 그대로 재사용할 계획.
