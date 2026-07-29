"""
Budget Agent - FastAPI backend entrypoint.

Run locally with:
    uvicorn app:app --reload --port 8000

Docs available at http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from api import hotels, restaurants, weather, currency, transport, budget

app = FastAPI(
    title="Budget Agent API",
    description="AI-powered travel budget planning engine for Indian destinations.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        # Don't crash the whole API if Postgres isn't up yet - endpoints that need
        # it will report a clear 503 instead, everything else still works.
        print(f"[startup] Warning: could not initialize database - {e}")


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "status": "running",
        "gemini_enabled": settings.GEMINI_ENABLED,
        "geoapify_enabled": settings.GEOAPIFY_ENABLED,
        "ors_enabled": settings.ORS_ENABLED,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(hotels.router)
app.include_router(restaurants.router)
app.include_router(weather.router)
app.include_router(currency.router)
app.include_router(transport.router)
app.include_router(budget.router)
