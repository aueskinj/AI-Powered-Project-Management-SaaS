from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_active_user, require_role
from app.models.user import UserPublic, UserRole, to_user_public

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: dict = Depends(get_current_active_user)):
    return to_user_public(current_user).model_dump()


@router.get("/admin-only", response_model=dict)
async def admin_only(current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    return {
        "message": "Admin access granted",
        "user": to_user_public(current_user).model_dump(),
    }
