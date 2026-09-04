from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.assessments import router as assessments_router


app = FastAPI(
    title="AI Interview Copilot API",
    version="0.5.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    assessments_router
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-interview-copilot-api",
        "version": "0.5.0",
    }