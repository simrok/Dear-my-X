-- Dear my X — Postgres 초기화 스크립트
-- docker-entrypoint-initdb.d/ 에 마운트되어 컨테이너 최초 기동 시 1회 실행됨.
-- pgvector 확장만 활성화하고, 실제 스키마는 alembic 마이그레이션으로 관리한다.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
