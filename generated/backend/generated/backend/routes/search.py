from fastapi import APIRouter, Query
from database import db
from core.config import settings

router = APIRouter()

@router.get("")
async def search(q: str = Query(...), limit: int = 20, offset: int = 0):
    # Try OpenSearch via settings.OPENSEARCH_URL
    if settings.OPENSEARCH_URL:
        try:
            # placeholder: call OpenSearch client
            # from opensearchpy import OpenSearch
            # client = OpenSearch(settings.OPENSEARCH_URL)
            # resp = client.search(body={...})
            return {"source": "opensearch", "hits": []}
        except Exception:
            pass
    # fallback to MongoDB text index search
    cursor = db["projects"].find({"$text": {"$search": q}}).skip(offset).limit(limit)
    items = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        items.append(doc)
    return {"source": "mongodb", "hits": items}