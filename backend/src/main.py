"""
R³ Diary System - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables - 명시적 경로 지정
_env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=_env_path)

_is_production = os.getenv("ENVIRONMENT", "development") == "production"

# Create FastAPI app
app = FastAPI(
    title="R³ Diary API",
    description="Rhythm-based personalized diary system API",
    version="0.1.0",
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
)

# CORS configuration - 개발 환경용 (프로덕션에서는 환경변수 사용)
_cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5000")
_cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=3600,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if _is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# OPTIONS 요청 전역 핸들러 (CORS preflight 명시적 처리)
@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    """Handle all OPTIONS requests for CORS preflight"""
    origin = request.headers.get("origin", "")
    allowed = origin if origin in _cors_origins else (_cors_origins[0] if _cors_origins else "")
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": allowed,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
            "Access-Control-Max-Age": "3600",
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "0.2.0",  # 버전 업데이트하여 배포 확인
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
from src.api import auth, profile, daily, monthly, logs, profiles, surveys, webhook, forms
# PDF router disabled on Windows (WeasyPrint requires GTK+)
# from src.api import pdf

# Register API routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(daily.router)
app.include_router(monthly.router)
app.include_router(logs.router)
app.include_router(profiles.router)
app.include_router(surveys.router)
app.include_router(webhook.router)
app.include_router(forms.router)
# app.include_router(pdf.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
