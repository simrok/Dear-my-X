"""initial schema (users, personas, chat_rooms, messages, uploads, memory_chunks)

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-06

이 마이그레이션은:
    1) 필요한 PostgreSQL 확장(vector, uuid-ossp, pg_trgm)을 멱등하게 보장.
    2) 모든 테이블을 의존성 순서로 생성 (FK = ON DELETE CASCADE).
    3) 조회 패턴에 맞춘 일반 인덱스를 추가.
    4) memory_chunks.embedding 에 HNSW + vector_cosine_ops 인덱스를 추가.

임베딩 차원은 1536 (OpenAI text-embedding-3-small). 다른 모델로 바꾸려면
별도의 ALTER 마이그레이션을 만든다.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


EMBEDDING_DIM = 1536


# ---------------------------------------------------------------------------
# upgrade
# ---------------------------------------------------------------------------
def upgrade() -> None:
    # 1) Extensions ----------------------------------------------------------
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2) users ---------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 3) personas ------------------------------------------------------------
    op.create_table(
        "personas",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_personas_user_id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("relation_type", sa.String(length=40), nullable=False),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("speaking_style", sa.Text(), nullable=True),
        sa.Column("profile_image_url", sa.String(length=1024), nullable=True),
        sa.Column("safety_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_personas_user_id", "personas", ["user_id"])
    # 홈 화면: 사용자별 최신순 정렬
    op.create_index(
        "ix_personas_user_id_created_at",
        "personas",
        ["user_id", sa.text("created_at DESC")],
    )

    # 4) chat_rooms ----------------------------------------------------------
    op.create_table(
        "chat_rooms",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE", name="fk_chat_rooms_user_id"),
            nullable=False,
        ),
        sa.Column(
            "persona_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "personas.id", ondelete="CASCADE", name="fk_chat_rooms_persona_id"
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_chat_rooms_user_id", "chat_rooms", ["user_id"])
    op.create_index("ix_chat_rooms_persona_id", "chat_rooms", ["persona_id"])
    # 홈 / 채팅 목록: 최근 활동 순
    op.create_index(
        "ix_chat_rooms_user_id_updated_at",
        "chat_rooms",
        ["user_id", sa.text("updated_at DESC")],
    )

    # 5) messages ------------------------------------------------------------
    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "chat_room_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "chat_rooms.id", ondelete="CASCADE", name="fk_messages_chat_room_id"
            ),
            nullable=False,
        ),
        sa.Column("sender_type", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "sender_type IN ('user', 'persona')",
            name="ck_messages_sender_type",
        ),
    )
    op.create_index("ix_messages_chat_room_id", "messages", ["chat_room_id"])
    # 채팅방 별 최근 N 개 메시지 조회용 복합 인덱스 (DESC)
    op.create_index(
        "ix_messages_chat_room_id_created_at",
        "messages",
        ["chat_room_id", sa.text("created_at DESC")],
    )

    # 6) conversation_uploads ------------------------------------------------
    op.create_table(
        "conversation_uploads",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="CASCADE", name="fk_uploads_user_id"
            ),
            nullable=False,
        ),
        sa.Column(
            "persona_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "personas.id", ondelete="CASCADE", name="fk_uploads_persona_id"
            ),
            nullable=False,
        ),
        sa.Column("file_url", sa.String(length=1024), nullable=False),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default=sa.text("'pending'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('pending','parsing','embedding','completed','failed')",
            name="ck_uploads_status",
        ),
    )
    op.create_index("ix_uploads_user_id", "conversation_uploads", ["user_id"])
    op.create_index("ix_uploads_persona_id", "conversation_uploads", ["persona_id"])
    op.create_index("ix_uploads_status", "conversation_uploads", ["status"])

    # 7) memory_chunks -------------------------------------------------------
    op.create_table(
        "memory_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="CASCADE", name="fk_memory_chunks_user_id"
            ),
            nullable=False,
        ),
        sa.Column(
            "persona_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "personas.id", ondelete="CASCADE", name="fk_memory_chunks_persona_id"
            ),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("speaker", sa.String(length=80), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_memory_chunks_user_id", "memory_chunks", ["user_id"])
    op.create_index("ix_memory_chunks_persona_id", "memory_chunks", ["persona_id"])

    # pgvector HNSW 인덱스 — cosine 유사도 검색용
    # alembic create_index 가 USING / opclass 를 직접 지원하지 않으므로 raw SQL.
    # m=16, ef_construction=64 는 pgvector 권장 기본값. 추후 워크로드에 맞게 튜닝.
    op.execute(
        """
        CREATE INDEX ix_memory_chunks_embedding_hnsw_cosine
            ON memory_chunks
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """
    )


# ---------------------------------------------------------------------------
# downgrade
# ---------------------------------------------------------------------------
def downgrade() -> None:
    # 인덱스/테이블은 CASCADE 로 따라가지만, 명시적으로 drop 해서 안전하게.
    op.execute("DROP INDEX IF EXISTS ix_memory_chunks_embedding_hnsw_cosine;")
    op.drop_index("ix_memory_chunks_persona_id", table_name="memory_chunks")
    op.drop_index("ix_memory_chunks_user_id", table_name="memory_chunks")
    op.drop_table("memory_chunks")

    op.drop_index("ix_uploads_status", table_name="conversation_uploads")
    op.drop_index("ix_uploads_persona_id", table_name="conversation_uploads")
    op.drop_index("ix_uploads_user_id", table_name="conversation_uploads")
    op.drop_table("conversation_uploads")

    op.drop_index("ix_messages_chat_room_id_created_at", table_name="messages")
    op.drop_index("ix_messages_chat_room_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_chat_rooms_user_id_updated_at", table_name="chat_rooms")
    op.drop_index("ix_chat_rooms_persona_id", table_name="chat_rooms")
    op.drop_index("ix_chat_rooms_user_id", table_name="chat_rooms")
    op.drop_table("chat_rooms")

    op.drop_index("ix_personas_user_id_created_at", table_name="personas")
    op.drop_index("ix_personas_user_id", table_name="personas")
    op.drop_table("personas")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # 확장은 의도적으로 drop 하지 않는다 (다른 DB 객체가 의존할 수 있음).
