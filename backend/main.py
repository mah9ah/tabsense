from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from db.database import init_db
from api import tabs, summaries, inactivity, events, settings as settings_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for TabSense — AI-powered tab & app productivity assistant.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()


# ── Routers ────────────────────────────────────────────────────────────────────
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