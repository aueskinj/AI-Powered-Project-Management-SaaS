from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import get_settings
from app.schemas.auth import TokenPayload


class TokenError(Exception):
    pass


def _create_token(subject: str, token_type: str, role: str, expires_delta: timedelta, jti: str | None) -> tuple[str, int, str | None]:
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    if jti is not None:
        payload["jti"] = jti

    settings = get_settings()
    encoded_token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_token, int(expires_at.timestamp()), jti


def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    token, _, _ = _create_token(
        subject=subject,
        token_type="access",
        role=role,
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
        jti=None,
    )
    return token


def create_refresh_token(subject: str, role: str) -> tuple[str, str, int]:
    settings = get_settings()
    jti = str(uuid4())
    token, exp_ts, _ = _create_token(
        subject=subject,
        token_type="refresh",
        role=role,
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
        jti=jti,
    )
    return token, jti, exp_ts


def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise TokenError("Invalid token") from exc

    try:
        return TokenPayload.model_validate(payload)
    except Exception as exc:
        raise TokenError("Invalid token payload") from exc
