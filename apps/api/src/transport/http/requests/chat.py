from pydantic import Field

from src.transport.http.requests.common import StrictRequestModel


class ChatSessionCreateRequest(StrictRequestModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)


class ChatMessageCreateRequest(StrictRequestModel):
    message: str = Field(min_length=1, max_length=2000)
    timezone: str
