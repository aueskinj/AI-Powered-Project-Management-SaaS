from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt_service import TokenError, create_access_token, create_refresh_token, decode_token
from app.auth.token_store import is_refresh_token_active, revoke_refresh_token, store_refresh_token
from app.core.security import hash_password, verify_password
from app.db.mongo import get_database
from app.db.redis import get_redis_client
from app.models.user import UserPublic, to_user_public
from app.schemas.auth import MessageResponse, RefreshTokenRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    database = get_database()

    existing_user = await database["users"].find_one({"email": payload.email.lower()})
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user_doc = {
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "full_name": payload.full_name,
        "role": payload.role.value,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await database["users"].insert_one(user_doc)
    created_user = await database["users"].find_one({"_id": result.inserted_id})
    return to_user_public(created_user).model_dump()


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    database = get_database()
    redis_client = get_redis_client()

    user_doc = await database["users"].find_one({"email": form_data.username.lower()})
    if user_doc is None or not verify_password(form_data.password, user_doc["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user_doc.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    subject = str(user_doc["_id"])
    role = user_doc["role"]

    access_token = create_access_token(subject=subject, role=role)
    refresh_token, refresh_jti, refresh_exp = create_refresh_token(subject=subject, role=role)
    await store_refresh_token(redis_client, refresh_jti, subject, refresh_exp)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest):
    database = get_database()
    redis_client = get_redis_client()

    try:
        token_payload = decode_token(payload.refresh_token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if token_payload.type != "refresh" or token_payload.jti is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if not await is_refresh_token_active(redis_client, token_payload.jti, token_payload.sub):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is inactive")

    try:
        user_object_id = ObjectId(token_payload.sub)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    user_doc = await database["users"].find_one({"_id": user_object_id})
    if user_doc is None or not user_doc.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    await revoke_refresh_token(redis_client, token_payload.jti)

    subject = str(user_doc["_id"])
    role = user_doc["role"]
    access_token = create_access_token(subject=subject, role=role)
    refresh_token, refresh_jti, refresh_exp = create_refresh_token(subject=subject, role=role)
    await store_refresh_token(redis_client, refresh_jti, subject, refresh_exp)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(payload: RefreshTokenRequest):
    redis_client = get_redis_client()

    try:
        token_payload = decode_token(payload.refresh_token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if token_payload.type != "refresh" or token_payload.jti is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    await revoke_refresh_token(redis_client, token_payload.jti)
    return MessageResponse(message="Logged out successfully")
