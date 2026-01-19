"""
R³ Diary System - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="R³ Diary API",
    description="Rhythm-based personalized diary system API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "0.1.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "R³ Diary API",
        "docs": "/docs",
        "health": "/health"
    }

# Import API routers
from src.api import auth, profile, daily, monthly, logs, pdf

# Register API routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(daily.router)
app.include_router(monthly.router)
app.include_router(logs.router)
app.include_router(pdf.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
