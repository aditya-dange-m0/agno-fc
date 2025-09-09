from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import os

app = FastAPI()

# CORS Configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust accordingly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# MongoDB configuration
MONGO_DETAILS = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.get_default_database()

@app.get("/health")
async def health_check():
    return {"status": "Healthy"}

# Include your routers here (e.g., auth, laps)
 # app.include_router(auth.router)
 # app.include_router(laps.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)