"""Authentication routes: register and login."""

import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorCollection

from app.config import get_settings
from app.database import mongo
from app.models.user import Token, TokenData, UserCreate, UserPublic
from app.services.user_service import UserService, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_user_collection() -> AsyncIOMotorCollection:
    return mongo.get_collection("users")


def create_access_token(user_id: str, email: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + (expires_delta or timedelta(days=settings.jwt_expire_days))
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> TokenData:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return TokenData(user_id=payload.get("sub"), email=payload.get("email"))
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


@router.post("/register", response_model=Token, status_code=201)
async def register(
    data: UserCreate,
    collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> Token:
    svc = UserService(collection)
    existing = await svc.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await svc.create(data)
    token = create_access_token(user.id or "", user.email)
    return Token(access_token=token, user=svc.to_public(user))


@router.post("/login", response_model=Token)
async def login(
    data: UserCreate,
    collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> Token:
    svc = UserService(collection)
    user = await svc.get_by_email(data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id or "", user.email)
    return Token(access_token=token, user=svc.to_public(user))
