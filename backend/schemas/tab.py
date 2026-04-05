from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator
from db.models import TabType, TabStatus, EventType


# ── Tab Schemas ────────────────────────────────────────────────────────────────

class TabCreate(BaseModel):
    type: TabType
    title: str
    url: Optional[str] = None
    app_name: Optional[str] = None
    favicon_url: Optional[str] = None
    inactivity_threshold: Optional[int] = None  # seconds
    auto_close_enabled: bool = False

    @field_validator("url", "favicon_url", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        return v or None


class TabUpdate(BaseModel):
    title: Optional[str] = None
    last_active_at: Optional[datetime] = None
    status: Optional[TabStatus] = None
    inactivity_threshold: Optional[int] = None
    auto_close_enabled: Optional[bool] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None


class TabResponse(BaseModel):
    id: int
    type: TabType
    title: str
    url: Optional[str]
    app_name: Optional[str]
    favicon_url: Optional[str]
    opened_at: datetime
    last_active_at: datetime
    closed_at: Optional[datetime]
    status: TabStatus
    ai_summary: Optional[str]
    ai_category: Optional[str]
    inactivity_threshold: Optional[int]
    auto_close_enabled: bool

    class Config:
        from_attributes = True


# ── Event Schemas ──────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    tab_id: int
    type: EventType
    details: Optional[str] = None  # JSON string


class EventResponse(BaseModel):
    id: int
    tab_id: int
    type: EventType
    timestamp: datetime
    details: Optional[str]

    class Config:
        from_attributes = True


# ── Settings Schemas ───────────────────────────────────────────────────────────

class UserSettingsUpdate(BaseModel):
    default_inactivity_threshold: Optional[int] = None
    auto_close_enabled_globally: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    ai_summaries_enabled: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    id: int
    default_inactivity_threshold: int
    auto_close_enabled_globally: bool
    notifications_enabled: bool
    ai_summaries_enabled: bool
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Inactivity Schemas ─────────────────────────────────────────────────────────

class InactiveTabResponse(BaseModel):
    tab: TabResponse
    inactive_for_seconds: float
    will_auto_close: bool


# ── Summary Schemas ────────────────────────────────────────────────────────────

class SummaryRequest(BaseModel):
    tab_id: int


class SummaryResponse(BaseModel):
    tab_id: int
    summary: str
    category: Optional[str]
