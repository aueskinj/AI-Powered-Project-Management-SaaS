from typing import Any, Callable

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt_service import TokenError, decode_token
from app.db.mongo import get_database
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_payload = decode_token(token)
    except TokenError as exc:
        raise credentials_exception from exc

    if token_payload.type != "access":
        raise credentials_exception

    try:
        user_object_id = ObjectId(token_payload.sub)
    except Exception as exc:
        raise credentials_exception from exc

    database = get_database()
    user_doc = await database["users"].find_one({"_id": user_object_id})
    if user_doc is None:
        raise credentials_exception

    return user_doc


async def get_current_active_user(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[UserRole | str]) -> Callable:
    normalized_roles = {
        role.value if isinstance(role, UserRole) else role for role in allowed_roles
    }

    async def _role_dependency(
        current_user: dict[str, Any] = Depends(get_current_active_user),
    ) -> dict[str, Any]:
        if current_user.get("role") not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return _role_dependency
