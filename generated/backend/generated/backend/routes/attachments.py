from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict
from services.storage import StorageService
from repositories.attachment_repository import register_attachment, get_attachment
from auth.deps import get_current_user
from workers.attachments_worker import process_attachment
from core.config import settings

router = APIRouter()

@router.post("/presign")
async def presign(payload: Dict, user: dict = Depends(get_current_user)):
    # payload: {filename, content_type, bucket?, key?}
    filename = payload.get("filename")
    content_type = payload.get("content_type") or "application/octet-stream"
    if not filename:
        raise HTTPException(status_code=400, detail="filename required")
    key = payload.get("key") or f"attachments/{filename}"
    bucket = payload.get("bucket") or settings.AWS_S3_BUCKET
    resp = await StorageService.generate_presigned_put(bucket, key, content_type)
    return {"upload": resp}

@router.post("/register")
async def register(payload: Dict, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    # metadata registration after successful upload
    doc = {
        "filename": payload.get("filename"),
        "mime_type": payload.get("mime_type"),
        "size": payload.get("size"),
        "project_id": payload.get("project_id"),
        "task_id": payload.get("task_id"),
        "s3_key": payload.get("s3_key"),
        "uploaded_by": user.get("id")
    }
    created = await register_attachment(doc)
    # enqueue background processing (virus scan, thumbnail)
    background_tasks.add_task(process_attachment, created["id"])
    return created

@router.get("/{attachment_id}/download")
async def download(attachment_id: str, user: dict = Depends(get_current_user)):
    att = await get_attachment(attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="Not found")
    url = await StorageService.generate_presigned_get(settings.AWS_S3_BUCKET, att.get("s3_key"))
    return {"download": url}