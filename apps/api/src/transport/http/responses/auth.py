from uuid import UUID

from pydantic import Field

from src.transport.http.responses.common import ResponseModel


class AuthUserResource(ResponseModel):
    id: UUID
    display_name: str = Field(alias="displayName")
    timezone: str


class LoginResource(ResponseModel):
    access_token: str = Field(alias="accessToken")
    expires_in: int = Field(alias="expiresIn")
    token_type: str = Field(alias="tokenType")
    user: AuthUserResource
