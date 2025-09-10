from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import db
from core.config import settings
import uuid

router = APIRouter()

class PresignRequest(BaseModel):
    filename: str
    content_type: Optional[str]

@router.post("/presign")
async def presign(req: PresignRequest):
    # Stubbed presigned URL generation. In production use boto3 or aiobotocore.
    key = f"attachments/{uuid.uuid4()}/{req.filename}"
    url = f"s3://{settings.S3_BUCKET}/{key}"
    return {"upload_url": url, "key": key}

class RegisterReq(BaseModel):
    filename: str
    mime_type: Optional[str]
    size: Optional[int]
    key: str
    project_id: Optional[str]
    task_id: Optional[str]

@router.post("/register")
async def register_attachment(payload: RegisterReq):
    doc = payload.model_dump()
    doc["uploaded_at"] = datetime.utcnow()
    res = await db["attachments"].insert_one(doc)
    return {"attachment_id": str(res.inserted_id)}