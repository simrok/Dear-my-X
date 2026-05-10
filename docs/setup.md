# 로컬 개발 환경 셋업

## 1. 전제

- Node.js 20+, pnpm 9+
- Python 3.11+
- Docker Desktop (또는 호환 런타임)
- Expo Go 앱 (실기기 테스트 시) 또는 iOS / Android 시뮬레이터

## 2. 클론 직후

```bash
# 의존성 (mobile + shared)
pnpm install

# 환경 변수
cp .env.example .env
cp apps/server/.env.example apps/server/.env
cp apps/mobile/.env.example apps/mobile/.env
```

각 .env 의 Supabase / Claude / OpenAI 키를 채운다. (Supabase 가 처음이라면 아래 "Supabase 프로젝트 준비" 섹션 먼저 진행)

## 2-1. Supabase 프로젝트 준비

Dear my X 의 인증은 Supabase Auth 가 권위(authority) 다. 서버는 발급된 JWT 만 검증하고, 모바일은 anon key 만 본다.

### 1) 프로젝트 만들기

1. https://supabase.com 에 가입 / 로그인
2. New Project 생성 (region 은 가까운 곳)
3. **Project Settings → API** 에서 다음 값을 메모:
   - `Project URL` (예: `https://abc123.supabase.co`)
   - `anon` `public` key
   - `service_role` `secret` key (절대 외부 노출 금지)
4. **Project Settings → API → JWT Settings** 에서:
   - `JWT Secret` 값을 메모 (아래 `SUPABASE_JWT_SECRET` 에 사용)

### 2) 이메일/비밀번호 인증 활성화

1. **Authentication → Providers → Email** 활성화
2. 개발 편의를 위해 **Confirm email** 옵션은 끄거나, 켰다면 받은 메일의 링크로 인증 완료
3. (선택) **Authentication → URL Configuration** 의 site URL 은 모바일 개발 시엔 무시 가능

### 3) 환경변수 채우기

**`apps/mobile/.env`** — 클라이언트가 직접 Supabase Auth 와 통신:

```bash
EXPO_PUBLIC_SUPABASE_URL=https://abc123.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOi...   # anon (public)
```

> ⚠️ **모바일에는 절대 `service_role` 키나 `JWT Secret` 을 넣지 마세요.**
> `EXPO_PUBLIC_*` 변수는 빌드에 포함되어 사용자 단말에 노출됩니다.

**`apps/server/.env`** — 서버는 JWT 만 검증:

```bash
SUPABASE_URL=https://abc123.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...               # 보통은 안 써도 되지만 보관
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...       # 추후 Storage 등 서버 작업용
SUPABASE_JWT_SECRET=super-long-jwt-secret     # /auth/me 의 JWT 검증에 필수
```

서버가 `SUPABASE_JWT_SECRET` 없이 뜨면 `/auth/me` 가 401 (`Server is not configured for authentication`) 을 반환한다.

## 3. DB

```bash
docker compose up -d db
```

## 4. 서버

```bash
cd apps/server
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# DB 스키마 적용 (최초 1회 + 새 마이그레이션이 추가될 때마다)
alembic upgrade head

uvicorn app.main:app --reload --port 8000
```

문서: http://localhost:8000/docs

## 5. DB 마이그레이션 (Alembic)

마이그레이션 파일은 `apps/server/alembic/versions/` 에 있고, 모델은 `app/models/*.py` 에 정의되어 있다.

### 적용 (가장 많이 쓰는 흐름)

```bash
cd apps/server
source .venv/bin/activate

# 최신 리비전까지 모두 적용
alembic upgrade head

# 한 단계만 올리기
alembic upgrade +1

# 직전으로 되돌리기
alembic downgrade -1

# 모두 되돌리기 (DB 비우기)
alembic downgrade base

# 현재 어디 와있는지 확인
alembic current
alembic history
```

### 적용 전 SQL 미리 보기 (offline 모드)

DB 에 실제 적용하지 않고 SQL 만 출력하고 싶을 때:

```bash
alembic upgrade head --sql > /tmp/migration.sql
```

### 새 마이그레이션 만들기

모델을 수정한 뒤 자동 감지로 초안을 생성:

```bash
alembic revision --autogenerate -m "add foo column"
```

> ⚠️ **주의**: pgvector `Vector` 타입과 HNSW / IVFFlat 인덱스, CHECK 제약은
> autogenerate 가 완전히는 잡지 못한다. 초안이 만들어지면
> `apps/server/alembic/versions/<rev>_*.py` 를 열어서:
> - `Vector(...)` 타입이 누락됐으면 직접 추가
> - 벡터 인덱스는 `op.execute("CREATE INDEX ... USING hnsw (...)")` 로 직접 작성
>
> 자동 생성 없이 빈 리비전을 만들고 싶다면:
> ```bash
> alembic revision -m "add foo"
> ```

### docker-compose 환경에서 마이그레이션

DB 가 docker 컨테이너에 떠 있고 서버는 호스트에서 실행 중이라면 그냥
`alembic upgrade head` 로 충분 (`apps/server/.env` 의 `DATABASE_URL` 이
`localhost:5432` 를 가리키도록).

서버까지 `docker compose up` 으로 띄운 경우:

```bash
docker compose exec server alembic upgrade head
```

### 초기 스키마 (`0001_initial`) 가 만드는 것

| 테이블 | 주요 인덱스 |
| --- | --- |
| `users` | `email` UNIQUE |
| `personas` | `user_id`, `(user_id, created_at DESC)` |
| `chat_rooms` | `user_id`, `persona_id`, `(user_id, updated_at DESC)` |
| `messages` | `chat_room_id`, `(chat_room_id, created_at DESC)` |
| `conversation_uploads` | `user_id`, `persona_id`, `status` |
| `memory_chunks` | `user_id`, `persona_id`, `embedding` HNSW (cosine) |

확장: `vector`, `uuid-ossp`, `pg_trgm` (멱등 생성).

## 6. 모바일

```bash
cd apps/mobile
pnpm start
```

- iOS 시뮬레이터: `i`
- Android 에뮬레이터: `a`
- 실기기: Expo Go 로 QR 스캔

실기기에서 서버에 접속하려면 `apps/mobile/.env` 의 `EXPO_PUBLIC_API_BASE_URL` 을 호스트 PC LAN IP 로 바꿔야 한다.

## 7. (대안) 한 번에 띄우기

```bash
docker compose up
```

→ DB + 서버가 함께 뜬다. 모바일은 별도로 실행.
