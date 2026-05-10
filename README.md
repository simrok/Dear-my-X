# Dear my X

> 과거의 대화에서 말투와 기억을 추출해, 사용자가 만든 가상 AI 페르소나와 대화하는 앱

**중요**: Dear my X는 실제 인물을 복제하거나 사칭하지 않습니다. 업로드된 대화 기록을 기반으로 한 **가상 AI 페르소나**를 제공합니다.

---

## Monorepo 구조

```
dear-my-x/
├── apps/
│   ├── mobile/          # React Native + Expo (TypeScript)
│   └── server/          # FastAPI + PostgreSQL/pgvector (Python)
├── packages/
│   └── shared/          # 공용 TypeScript 타입/상수 (mobile + 추후 web)
├── docker/              # Docker / Postgres 초기화 스크립트
├── docs/                # 아키텍처 문서
├── docker-compose.yml   # 로컬 개발용 컴포즈
├── package.json         # 워크스페이스 루트
└── pnpm-workspace.yaml  # pnpm workspaces 설정
```

추후 `apps/web` (Next.js 등) 추가 시 `packages/shared`를 그대로 재사용합니다.

---

## 기술 스택

| 영역 | 기술 |
| --- | --- |
| Mobile | React Native + Expo + TypeScript |
| Server | FastAPI (Python 3.11+) |
| DB | PostgreSQL 16 + `pgvector` |
| Auth | Supabase Auth |
| Storage | Supabase Storage (또는 S3) |
| AI Chat | Claude API (Anthropic) |
| Embedding | OpenAI `text-embedding-3-small` |
| Package Manager | pnpm (workspaces) |
| Container | Docker / docker-compose |

---

## 빠른 시작

### 1. 사전 준비

```bash
# pnpm 설치 (없다면)
npm i -g pnpm

# Python 3.11+ 와 Docker 설치 필요
```

### 2. 환경 변수 설정

각 앱의 `.env.example`을 복사해서 사용합니다.

```bash
cp .env.example .env
cp apps/mobile/.env.example apps/mobile/.env
cp apps/server/.env.example apps/server/.env
```

**Supabase 환경변수 (필수)**

| 위치 | 변수 | 비고 |
| --- | --- | --- |
| `apps/mobile/.env` | `EXPO_PUBLIC_SUPABASE_URL` | 클라이언트 노출됨 (OK) |
| `apps/mobile/.env` | `EXPO_PUBLIC_SUPABASE_ANON_KEY` | 클라이언트 노출됨 (OK) |
| `apps/server/.env` | `SUPABASE_URL` | |
| `apps/server/.env` | `SUPABASE_JWT_SECRET` | **서버 전용. 절대 모바일 X** |
| `apps/server/.env` | `SUPABASE_SERVICE_ROLE_KEY` | **서버 전용. 절대 모바일 X** |

값을 어디서 가져오는지 / Supabase 프로젝트 만드는 법은 [`docs/setup.md` § 2-1 Supabase 프로젝트 준비](./docs/setup.md#2-1-supabase-프로젝트-준비) 참고.

### 3. 의존성 설치

```bash
# 루트에서 mobile + shared 한번에
pnpm install

# server는 별도
cd apps/server
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 로컬 개발

```bash
# Postgres + pgvector 띄우기
docker compose up -d db

# 서버 실행
cd apps/server
uvicorn app.main:app --reload --port 8000

# 모바일 실행 (별도 터미널)
cd apps/mobile
pnpm start
```

또는 한 번에:

```bash
docker compose up
```

---

## 아키텍처 원칙

1. **모노레포** — `apps/` (실행 가능한 앱) 와 `packages/` (재사용 가능한 라이브러리) 를 분리합니다.
2. **모바일 우선** — 디자인과 UX는 모바일 기준으로 설계되며, 추후 웹은 `packages/shared`의 타입과 로직을 재사용합니다.
3. **TypeScript 우선** — 모바일/공용 패키지는 모두 TS. 서버 ↔ 클라이언트 간 인터페이스는 `packages/shared`로 동기화합니다.
4. **AI 로직 분리** — `apps/server/app/ai/`에 AI(Claude, embedding, RAG, masking, parsing) 관련 로직을 별도로 두어, 일반 비즈니스 로직(`services/`)과 분리합니다.
5. **Repository / Service / Controller** — 데이터 접근(`repositories`), 도메인 로직(`services`), API 엔드포인트(`api/v1`) 의 책임을 분리합니다.
6. **외부 의존성 격리** — Supabase, Claude, OpenAI 등 외부 SDK는 `integrations/` 또는 `ai/clients/`에 어댑터로 두어, 비즈니스 로직이 외부 SDK에 직접 의존하지 않도록 합니다.

자세한 내용은 [`docs/architecture.md`](./docs/architecture.md) 참고.

---

## 라이선스 / 안전성 고지

이 앱은 **실제 인물 복제 / 사칭을 위한 도구가 아닙니다.** 업로드되는 대화 기록은 사용자가 사용 권한을 보유한 자료여야 합니다. 자세한 안전 정책은 추후 `docs/safety.md`에 정리합니다.
