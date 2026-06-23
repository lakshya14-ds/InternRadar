"""Authentication routes: register and login."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

from app.config import get_settings
from app.database import mongo
from app.models.user import Token, TokenData, UserCreate
from app.services.user_service import UserService, verify_password

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

def get_user_collection() -> AsyncIOMotorCollection:
    return mongo.get_collection("users")

def create_access_token(
    user_id: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()

    expire = datetime.now(UTC) + (
        expires_delta or timedelta(days=settings.jwt_expire_days)
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm="HS256",
    )

def decode_token(token: str) -> TokenData:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
        )

        return TokenData(
            user_id=payload.get("sub"),
            email=payload.get("email"),
        )

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> Token:
    svc = UserService(collection)

    existing = await svc.get_by_email(data.email)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await svc.create(data)

    token = create_access_token(
        str(user.id),
        user.email,
    )

    return Token(
        access_token=token,
        user=svc.to_public(user),
    )

@router.post(
    "/login",
    response_model=Token,
)
async def login(
    data: LoginRequest,
    collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> Token:
    svc = UserService(collection)

    user = await svc.get_by_email(data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        str(user.id),
        user.email,
    )

    return Token(
        access_token=token,
        user=svc.to_public(user),
    )
