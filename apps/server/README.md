# Dear my X — Server (FastAPI)

가상 AI 페르소나 채팅 앱의 백엔드 API.

## 레이어드 아키텍처

```
api/v1            ← Controller  (HTTP 라우트, 입력 검증, 응답 직렬화)
  ↓
services/         ← Service     (도메인 로직, 트랜잭션 단위 작업)
  ↓
repositories/     ← Repository  (DB 접근만 담당, ORM 호출)
  ↓
models/           ← SQLAlchemy ORM 모델

ai/               ← AI 전용 로직 (Claude, OpenAI, RAG, 마스킹, 카카오 파서 등)
                    services/ 가 ai/ 를 호출하지만, ai/ 는 services/ 를 모르도록 유지
integrations/     ← Supabase, S3 등 외부 SDK 어댑터
core/             ← 설정, 보안, 로깅, 공통 예외
db/               ← 세션, Base, pgvector 헬퍼
schemas/          ← Pydantic (request / response DTO)
```

> **AI 로직은 `app/ai/` 에 격리**되어 있습니다. 일반 비즈니스 로직(`services/`)은 AI 어댑터를 의존성 주입으로 받아 사용합니다.

## 폴더 구조

```
apps/server/
├── app/
│   ├── main.py                  # FastAPI 앱 팩토리
│   ├── core/                    # config, logging, security, exceptions
│   ├── db/                      # 세션, Base, pgvector 헬퍼
│   ├── models/                  # SQLAlchemy 모델
│   ├── schemas/                 # Pydantic DTO
│   ├── repositories/            # 데이터 접근 계층
│   ├── services/                # 도메인 서비스
│   ├── ai/
│   │   ├── clients/             # Claude / OpenAI 어댑터
│   │   ├── prompts/             # 프롬프트 템플릿
│   │   ├── rag/                 # 검색기, 랭커
│   │   ├── parsers/             # 카카오톡 파서
│   │   ├── masking/             # 개인정보 마스킹
│   │   └── chunkers/            # 대화 chunk 분리
│   ├── api/
│   │   ├── deps.py              # 공통 의존성 (DB, 현재 사용자)
│   │   └── v1/                  # 버전드 라우트
│   ├── integrations/            # Supabase, Storage 등 외부 어댑터
│   ├── workers/                 # (추후) 비동기 작업
│   └── utils/
├── alembic/                     # DB 마이그레이션
├── tests/
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## 실행

```bash
# 가상환경
python -m venv .venv && source .venv/bin/activate

# 설치
pip install -r requirements.txt

# 환경변수
cp .env.example .env

# 로컬 DB (루트에서)
docker compose up -d db

# 마이그레이션 적용
alembic upgrade head

# 서버
uvicorn app.main:app --reload --port 8000
```

OpenAPI 문서: http://localhost:8000/docs

## 마이그레이션 (Alembic)

```bash
# 적용
alembic upgrade head

# 되돌리기
alembic downgrade -1

# 새 리비전 (모델 변경 후)
alembic revision --autogenerate -m "describe change"
```

> ⚠️ pgvector `Vector` 타입, HNSW / IVFFlat 인덱스, CHECK 제약은 autogenerate 가
> 완전히 잡지 못하므로 생성된 파일을 수동 보정해야 한다. 자세한 내용은
> [`../../docs/setup.md`](../../docs/setup.md) 의 "DB 마이그레이션" 섹션 참고.

현재 적용되는 초기 스키마는 `apps/server/alembic/versions/0001_initial.py`.
