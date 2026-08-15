from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.config.settings import Settings
from src.persistence.models.auth import AuthCredential, RefreshSession
from src.persistence.models.enums import UserStatus
from src.persistence.models.user import AppUser
from src.persistence.repositories.auth import AuthRepository
from src.persistence.repositories.users import UserRepository
from src.shared.errors.api_error import ApiError
from src.shared.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    issue_access_token,
    verify_password,
)


class AuthService:
    def __init__(self, users: UserRepository, auth: AuthRepository, settings: Settings) -> None:
        self._users = users
        self._auth = auth
        self._settings = settings

    @staticmethod
    def normalized_email(email: str) -> str:
        return email.strip().lower()

    async def signup(self, email: str, password: str, display_name: str, timezone: str) -> AppUser:
        normalized = self.normalized_email(email)
        if await self._users.get_active_by_email(normalized) is not None:
            raise ApiError(
                409, "EMAIL_ALREADY_REGISTERED", "An account with this email already exists."
            )
        user = AppUser(
            email=normalized,
            display_name=display_name,
            timezone_name=timezone,
            status=UserStatus.ACTIVE,
        )
        self._users.add(user)
        await (
            self._users._session.flush()
        )  # The database generates the tenant identifier atomically.
        await self._users._session.execute(
            __import__("sqlalchemy").text("SELECT set_config('app.user_id', :user_id, true)"),
            {"user_id": str(user.id)},
        )
        self._auth.add_credential(
            AuthCredential(user_id=user.id, password_hash=await hash_password(password))
        )
        return user

    async def login(
        self, email: str, password: str, user_agent: str | None = None
    ) -> tuple[AppUser, str, str]:
        user = await self._users.get_active_by_email(self.normalized_email(email))
        credential = await self._auth.get_credential(user.id) if user is not None else None
        valid = credential is not None and await verify_password(password, credential.password_hash)
        now = datetime.now(UTC)
        if (
            not valid
            or credential is None
            or (credential.locked_until is not None and credential.locked_until > now)
        ):
            if user is not None:
                count = credential.failed_login_count + 1 if credential is not None else 1
                await self._auth.record_failed_login(
                    user.id, now + timedelta(minutes=15) if count >= 5 else None
                )
            raise ApiError(401, "INVALID_CREDENTIALS", "Invalid email or password.")
        assert user is not None
        await self._auth.reset_failed_login(user.id)
        await self._users._session.execute(
            __import__("sqlalchemy").text("SELECT set_config('app.user_id', :user_id, true)"),
            {"user_id": str(user.id)},
        )
        refresh = generate_refresh_token()
        self._auth.add_refresh_session(
            RefreshSession(
                user_id=user.id,
                token_hash=hash_refresh_token(refresh),
                expires_at=now + timedelta(days=self._settings.refresh_token_ttl_days),
                user_agent=user_agent,
            )
        )
        return user, issue_access_token(user.id, self._settings), refresh

    async def refresh(self, token: str, user_agent: str | None = None) -> tuple[str, str]:
        now = datetime.now(UTC)
        token_hash = hash_refresh_token(token)
        lookup = await self._auth.lookup_refresh_session(token_hash)
        if lookup is None:
            raise ApiError(401, "UNAUTHORIZED", "A valid refresh session is required.")
        _, user_id = lookup
        await self._users._session.execute(
            __import__("sqlalchemy").text("SELECT set_config('app.user_id', :user_id, true)"),
            {"user_id": str(user_id)},
        )
        session = await self._auth.get_refresh_session(token_hash)
        if session is None or session.expires_at <= now:
            raise ApiError(401, "UNAUTHORIZED", "A valid refresh session is required.")
        if session.revoked_at is not None:
            await self._auth.revoke_all_active(session.user_id, now)
            raise ApiError(401, "UNAUTHORIZED", "A valid refresh session is required.")
        user = await self._users.get_active(session.user_id)
        if user is None:
            raise ApiError(401, "UNAUTHORIZED", "A valid refresh session is required.")
        await self._auth.revoke_refresh_session(session.id, now)
        replacement = generate_refresh_token()
        self._auth.add_refresh_session(
            RefreshSession(
                user_id=user.id,
                token_hash=hash_refresh_token(replacement),
                expires_at=now + timedelta(days=self._settings.refresh_token_ttl_days),
                user_agent=user_agent,
            )
        )
        return issue_access_token(user.id, self._settings), replacement

    async def logout(self, user_id: UUID, token: str | None) -> None:
        if token:
            session = await self._auth.get_refresh_session(hash_refresh_token(token))
            if session is not None and session.user_id == user_id:
                await self._auth.revoke_refresh_session(session.id, datetime.now(UTC))
