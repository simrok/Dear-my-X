"""페르소나 라우트 (controller).

도메인 로직은 PersonaService 에 위임.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.api.deps import CurrentUserDep, get_persona_service
from app.schemas.persona import PersonaCreate, PersonaRead, PersonaUpdate
from app.services.persona_service import PersonaService

router = APIRouter()

PersonaServiceDep = Annotated[PersonaService, Depends(get_persona_service)]


@router.post("", response_model=PersonaRead, status_code=201)
async def create_persona(
    body: PersonaCreate,
    user: CurrentUserDep,
    service: PersonaServiceDep,
) -> PersonaRead:
    persona = await service.create(user_id=user.id, data=body)
    return PersonaRead.model_validate(persona)


@router.get("", response_model=list[PersonaRead])
async def list_personas(
    user: CurrentUserDep,
    service: PersonaServiceDep,
) -> list[PersonaRead]:
    items = await service.list_mine(user_id=user.id)
    return [PersonaRead.model_validate(p) for p in items]


@router.get("/{persona_id}", response_model=PersonaRead)
async def get_persona(
    persona_id: uuid.UUID,
    user: CurrentUserDep,
    service: PersonaServiceDep,
) -> PersonaRead:
    persona = await service.get_owned(user_id=user.id, persona_id=persona_id)
    return PersonaRead.model_validate(persona)


@router.patch("/{persona_id}", response_model=PersonaRead)
async def update_persona(
    persona_id: uuid.UUID,
    body: PersonaUpdate,
    user: CurrentUserDep,
    service: PersonaServiceDep,
) -> PersonaRead:
    persona = await service.update(user_id=user.id, persona_id=persona_id, data=body)
    return PersonaRead.model_validate(persona)


@router.delete("/{persona_id}", status_code=204)
async def delete_persona(
    persona_id: uuid.UUID,
    user: CurrentUserDep,
    service: PersonaServiceDep,
) -> Response:
    await service.delete(user_id=user.id, persona_id=persona_id)
    return Response(status_code=204)
