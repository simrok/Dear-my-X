from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel

RelationType = Literal["ex_partner", "friend", "family", "other"]


class PersonaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    relation_type: RelationType
    personality: str | None = None
    speaking_style: str | None = None
    profile_image_url: str | None = None
    safety_notes: str | None = None
    consent_virtual_persona: bool
    consent_data_rights: bool


class PersonaUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    relation_type: RelationType | None = None
    personality: str | None = None
    speaking_style: str | None = None
    profile_image_url: str | None = None
    safety_notes: str | None = None


class PersonaRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    relation_type: str
    personality: str | None
    speaking_style: str | None
    profile_image_url: str | None
    safety_notes: str | None
    created_at: datetime
    updated_at: datetime
