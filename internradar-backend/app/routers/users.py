"""User profile, preferences, and bookmark routes."""

import logging

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database import mongo
from app.models.internship import InternshipInDB
from app.models.user import UserPublic, UserUpdate
from app.routers.auth import decode_token
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_collection() -> AsyncIOMotorCollection:
    return mongo.get_collection("users")


def get_bookmark_collection() -> AsyncIOMotorCollection:
    return mongo.get_collection("bookmarks")


def get_internship_collection() -> AsyncIOMotorCollection:
    return mongo.get_collection("internships")


async def current_user_id(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    data = decode_token(token)
    if not data.user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return data.user_id


@router.get("/me", response_model=UserPublic)
async def get_profile(
    user_id: str = Depends(current_user_id),
    collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> UserPublic:
    svc = UserService(collection)
    user = await svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return svc.to_public(user)


@router.put("/me", response_model=UserPublic)
async def update_profile(
    data: UserUpdate,
    user_id: str = Depends(current_user_id),
    collection: AsyncIOMotorCollection = Depends(get_user_collection),
) -> UserPublic:
    svc = UserService(collection)
    user = await svc.update(user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return svc.to_public(user)


@router.get("/me/bookmarks", response_model=list[InternshipInDB])
async def list_bookmarks(
    user_id: str = Depends(current_user_id),
    bookmark_col: AsyncIOMotorCollection = Depends(get_bookmark_collection),
    intern_col: AsyncIOMotorCollection = Depends(get_internship_collection),
) -> list[InternshipInDB]:
    cursor = bookmark_col.find({"user_id": user_id})
    bookmarks = [doc async for doc in cursor]
    internship_ids = []
    for b in bookmarks:
        try:
            internship_ids.append(ObjectId(b["internship_id"]))
        except (InvalidId, KeyError):
            pass
    if not internship_ids:
        return []
    cursor2 = intern_col.find({"_id": {"$in": internship_ids}})
    return [InternshipInDB.model_validate(doc) async for doc in cursor2]


@router.post("/me/bookmarks/{internship_id}", status_code=201)
async def add_bookmark(
    internship_id: str,
    user_id: str = Depends(current_user_id),
    bookmark_col: AsyncIOMotorCollection = Depends(get_bookmark_collection),
) -> dict:
    existing = await bookmark_col.find_one({"user_id": user_id, "internship_id": internship_id})
    if existing:
        return {"saved": True}
    await bookmark_col.insert_one({"user_id": user_id, "internship_id": internship_id})
    return {"saved": True}


@router.delete("/me/bookmarks/{internship_id}")
async def remove_bookmark(
    internship_id: str,
    user_id: str = Depends(current_user_id),
    bookmark_col: AsyncIOMotorCollection = Depends(get_bookmark_collection),
) -> dict:
    await bookmark_col.delete_one({"user_id": user_id, "internship_id": internship_id})
    return {"removed": True}


@router.get("/me/bookmarks/ids")
async def bookmark_ids(
    user_id: str = Depends(current_user_id),
    bookmark_col: AsyncIOMotorCollection = Depends(get_bookmark_collection),
) -> list[str]:
    cursor = bookmark_col.find({"user_id": user_id}, {"internship_id": 1})
    return [doc["internship_id"] async for doc in cursor]
