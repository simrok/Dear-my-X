"""Generic repository base.

자주 쓰는 CRUD 패턴(get/list/create/update/delete) 만 추출.
도메인별 특수 쿼리는 각 리포지토리의 메서드로 추가한다.
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id_: uuid.UUID) -> ModelT | None:
        return await self.session.get(self.model, id_)

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **fields: Any) -> ModelT:
        obj = self.model(**fields)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, instance: ModelT, **fields: Any) -> ModelT:
        for k, v in fields.items():
            setattr(instance, k, v)
        await self.session.flush()
        return instance

    async def delete(self, id_: uuid.UUID) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == id_))  # type: ignore[attr-defined]
