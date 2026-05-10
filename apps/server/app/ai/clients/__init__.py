"""AI 모델 어댑터 (Claude / OpenAI 등)."""

from app.ai.clients.claude_client import ClaudeClient
from app.ai.clients.embedding_client import EmbeddingClient

__all__ = ["ClaudeClient", "EmbeddingClient"]
