from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app import face_detection
from app import user
from core import auth

app = FastAPI(
    title="Face detection API",
    description="Face Detection Backend for REST API.",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(face_detection.router, prefix="/app")
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
