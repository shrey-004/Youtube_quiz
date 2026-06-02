"""
main.py — Entry point for the FastAPI application.

This file creates the app instance, registers all route handlers,
and configures middleware. Think of it as the "front door" of your API.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging — this prints structured logs to your terminal
# In production you'd send logs to a service like Datadog or CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create the FastAPI app instance
# title and version appear in the auto-generated /docs page
app = FastAPI(
    title="YouTube Quiz Generator API",
    description="AI-powered quiz generation from YouTube videos",
    version="1.0.0",
)

# CORS middleware — this allows your Next.js frontend (running on
# localhost:3000) to make requests to your FastAPI backend (localhost:8000).
# Without this, the browser blocks cross-origin requests for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # Next.js dev server
        "https://your-app.vercel.app", # Your Vercel deployment (update later)
    ],
    allow_credentials=True,
    allow_methods=["*"],   # Allow GET, POST, PUT, DELETE etc.
    allow_headers=["*"],   # Allow Authorization headers (for JWT)
)


# Health check endpoint — always have one of these.
# Deployment platforms ping this to check if your app is alive.
@app.get("/health")
async def health_check():
    """Returns OK if the server is running."""
    logger.info("Health check called")
    return {"status": "ok", "message": "YouTube Quiz Generator API is running"}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to YouTube Quiz Generator API",
        "docs": "/docs",
        "health": "/health"
    }


# Log when the server starts
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 YouTube Quiz Generator API started")


logger.info("App module loaded")