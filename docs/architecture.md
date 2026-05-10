# Architecture

## 큰 그림

```
┌───────────────┐                ┌──────────────────────────┐
│  apps/mobile  │ ── HTTP+JWT ─▶ │       apps/server        │
│ (Expo + RN)   │                │  FastAPI (Python 3.11)   │
└──────┬────────┘                │  ┌────────┐  ┌────────┐  │
       │                         │  │ api/v1 │─▶│services│  │
       ▼                         │  └────────┘  └───┬────┘  │
┌───────────────┐                │              ┌───┴────┐  │
│  Supabase     │ ──Auth/Storage │              │  ai/   │  │
│  (Auth/Files) │                │              └───┬────┘  │
└───────────────┘                │              ┌───┴────┐  │
                                 │              │ repos  │  │
                                 │              └───┬────┘  │
                                 │                  ▼       │
                                 │  ┌──────────────────┐    │
                                 │  │ Postgres+pgvector│    │
                                 │  └──────────────────┘    │
                                 └───────┬──────────────────┘
                                         │
                                ┌────────┴────────┐
                                ▼                 ▼
                         Anthropic Claude   OpenAI Embedding
```

## 레이어 책임

| 레이어 | 책임 | 의존 방향 |
| --- | --- | --- |
| `api/v1` (Controller) | HTTP 라우팅 / 입력 검증 / 응답 직렬화 | → services |
| `services/` | 도메인 로직 / 트랜잭션 경계 / 권한 체크 | → repositories, ai/ (DI) |
| `repositories/` | 순수 DB 접근 (SQLAlchemy) | → models, db |
| `ai/` | 외부 모델 / 파서 / 마스킹 / RAG 어댑터 | self-contained |
| `integrations/` | Supabase / S3 등 외부 SDK 어댑터 | self-contained |
| `models/` | SQLAlchemy ORM | → db |
| `schemas/` | Pydantic DTO | self-contained |

핵심 원칙:
- **services 가 ai 를 호출**하되, ai 가 services 를 알지 않는다.
- **repositories 는 트랜잭션을 commit 하지 않는다.** services 가 결정한다.
- **외부 SDK 직접 의존 X** — Claude, OpenAI, Supabase 는 항상 `ai/clients/` 또는 `integrations/` 어댑터를 통해 사용.

## 모노레포

```
dear-my-x/
├── apps/
│   ├── mobile/      # Expo (TypeScript)
│   └── server/      # FastAPI (Python)
├── packages/
│   └── shared/      # 공용 TS 타입/상수
└── docker-compose.yml
```

추후 `apps/web` 추가 시 `packages/shared` 를 그대로 재사용한다.
공용 검증 로직(zod 등)이나 유틸이 늘어나면 `packages/` 아래에 새 패키지를 만든다.

## 환경 변수 분리

| 위치 | 용도 |
| --- | --- |
| `.env` (루트) | docker-compose 가 사용하는 DB / 포트 / 공유 변수 |
| `apps/server/.env` | 서버 전용 (DB URL, AI 키, Supabase 시크릿) |
| `apps/mobile/.env` | 모바일 전용 (`EXPO_PUBLIC_*` 만 클라이언트에 노출) |

비밀(서비스 롤 키 등)은 **반드시 서버 측에만** 두고, 모바일은 anon 키만 사용한다.

## RAG 흐름 (요약)

1. 사용자가 메시지 전송
2. `ChatService.send_message`
3. `MemoryRetriever.search` → embedding → `MemoryChunkRepository.search_similar` (pgvector cosine)
4. `build_system_prompt(persona, chunks)` → Claude
5. AI 응답 저장 + 반환

## DB 인덱스 (계획)

- `memory_chunks(persona_id)` 일반 인덱스
- `memory_chunks(embedding)` IVFFlat / HNSW (alembic 에서 수동 생성)
- `messages(chat_room_id, created_at desc)` 부분 인덱스
- `personas(user_id)` 일반 인덱스

## 확장 포인트

- **Web 추가**: `apps/web` 를 만들고 `@dear-my-x/shared` 를 임포트.
- **임베딩 제공자 교체**: `ai/clients/embedding_client.py` 의 Protocol 만 만족하면 OK.
- **Storage 교체**: `integrations/storage/` 의 `ObjectStorage` Protocol 구현체 추가.
- **Auth 교체**: `core/security.py` 의 토큰 검증 함수만 갈아끼우면 됨.
- **백그라운드 작업**: `app/workers/` 로 분리 (Celery / arq / rq 후보).
