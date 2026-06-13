"""Company API routes."""

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import APIRouter, Depends, HTTPException

from app.database import mongo
from app.models.company import CompanyInDB

router = APIRouter(prefix="/companies", tags=["companies"])


async def get_company_collection() -> AsyncIOMotorCollection:
    return mongo.get_collection("companies")


@router.get("", response_model=list[CompanyInDB])
async def list_companies(
    collection: AsyncIOMotorCollection = Depends(get_company_collection),
) -> list[CompanyInDB]:
    cursor = collection.find({"active": True}).sort("name", 1)
    return [CompanyInDB.model_validate(item) async for item in cursor]


@router.get("/{company_id}", response_model=CompanyInDB)
async def get_company(
    company_id: str,
    collection: AsyncIOMotorCollection = Depends(get_company_collection),
) -> CompanyInDB:
    try:
        object_id = ObjectId(company_id)
    except InvalidId as exc:
        raise HTTPException(status_code=400, detail="Invalid company id") from exc
    document = await collection.find_one({"_id": object_id})
    if document is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyInDB.model_validate(document)
