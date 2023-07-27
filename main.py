from fastapi import FastAPI
import uvicorn
from app import face_detection

app = FastAPI()
app.include_router(face_detection.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)
