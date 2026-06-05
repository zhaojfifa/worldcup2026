"""
WorldCup 2026 AI Intelligence Terminal — Backend API
AI data analysis service. Not a betting platform.
MTC = Platform loyalty points only. Not withdrawable. Not a financial asset.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import health, matches, tokens, data_source, admin, performance, assets, social, rankings

settings = get_settings()

app = FastAPI(
    title="WorldCup 2026 AI API",
    description=(
        "AI sports data analysis platform. "
        "Not a betting or gambling service. "
        "MTC points are platform loyalty points — not withdrawable, not transferable."
    ),
    version="0.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(health.router)
app.include_router(matches.router)
app.include_router(tokens.router)
app.include_router(data_source.router)
app.include_router(admin.router)
app.include_router(performance.router)
app.include_router(assets.router)
app.include_router(social.router)
app.include_router(rankings.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "service": "WorldCup 2026 AI Intelligence Terminal",
        "version": "0.6.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "compliance": "AI data analysis only. Not a betting service. MTC not withdrawable.",
    }
