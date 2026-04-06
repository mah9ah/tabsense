from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from core.config import settings
from core.security import limiter
from db.database import init_db
from api import tabs, summaries, inactivity, events, settings as settings_router, auth

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for TabSense — AI-powered tab & app productivity assistant.",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,   # Hide docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── Rate Limiting ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ───────────────────────────────────────────────────────────────────────
# OPTIONS must be included so preflight requests from Electron renderer succeed
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()


# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth.router)          # Public — login/register
app.include_router(tabs.router)
app.include_router(summaries.router)
app.include_router(inactivity.router)
app.include_router(events.router)
app.include_router(settings_router.router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

# ── Root route for testing ─────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "TabSense backend is running!"}