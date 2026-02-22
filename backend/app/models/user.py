from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


def to_user_public(user_doc: dict[str, Any]) -> UserPublic:
    created_at = user_doc.get("created_at")
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    return UserPublic(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=user_doc["role"],
        is_active=user_doc.get("is_active", True),
        created_at=created_at,
    )
