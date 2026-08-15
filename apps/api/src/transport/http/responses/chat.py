from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.persistence.models.enums import ChatRole


class ChatSessionResource(BaseModel):
    id: UUID
    title: str | None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ChatMessageResource(BaseModel):
    id: UUID
    role: ChatRole
    content: str
    created_at: datetime = Field(alias="createdAt")
