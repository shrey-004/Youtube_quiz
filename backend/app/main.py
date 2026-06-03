"""
main.py — Final version with all routers and database setup.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, quizzes, videos
from app.db.session import engine
from app.db import models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create all database tables on startup
# This is safe to run multiple times — it only creates tables
# that don't already exist (checkfirst=True is the default)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YouTube Quiz Generator API",
    description="AI-powered quiz generation from YouTube videos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(quizzes.router)
app.include_router(videos.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "YouTube Quiz Generator API is running"}


@app.get("/")
async def root():
    return {
        "message": "Welcome to YouTube Quiz Generator API",
        "docs": "/docs",
        "health": "/health",
    }


@app.on_event("startup")
async def startup_event():
    logger.info("YouTube Quiz Generator API started — tables verified")