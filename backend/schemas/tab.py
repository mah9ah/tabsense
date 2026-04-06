from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator
from db.models import TabType, TabStatus, EventType
from core.sanitize import (
    sanitize_text, sanitize_url,
    MAX_TITLE_LEN, MAX_URL_LEN, MAX_APP_LEN, MAX_DETAILS_LEN, MAX_SEARCH_LEN,
)


# ── Tab Schemas ────────────────────────────────────────────────────────────────

class TabCreate(BaseModel):
    type: TabType
    title: str
    url: Optional[str] = None
    app_name: Optional[str] = None
    favicon_url: Optional[str] = None
    inactivity_threshold: Optional[int] = None  # seconds
    auto_close_enabled: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        result = sanitize_text(v, MAX_TITLE_LEN, "title")
        if not result:
            raise ValueError("title cannot be empty.")
        return result

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        return sanitize_url(v)

    @field_validator("favicon_url")
    @classmethod
    def validate_favicon_url(cls, v):
        return sanitize_url(v)

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, v):
        return sanitize_text(v, MAX_APP_LEN, "app_name")

    @field_validator("inactivity_threshold")
    @classmethod
    def validate_threshold(cls, v):
        if v is not None and (v < 30 or v > 86400):
            raise ValueError("inactivity_threshold must be between 30 and 86400 seconds.")
        return v

    @model_validator(mode="after")
    def check_url_or_app(self):
        if self.type == TabType.browser_tab and not self.url:
            raise ValueError("browser_tab requires a url.")
        if self.type == TabType.desktop_app and not self.app_name:
            raise ValueError("desktop_app requires an app_name.")
        return self


class TabUpdate(BaseModel):
    title: Optional[str] = None
    last_active_at: Optional[datetime] = None
    status: Optional[TabStatus] = None
    inactivity_threshold: Optional[int] = None
    auto_close_enabled: Optional[bool] = None
    ai_summary: Optional[str] = None
    ai_category: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        return sanitize_text(v, MAX_TITLE_LEN, "title")

    @field_validator("ai_summary")
    @classmethod
    def validate_summary(cls, v):
        return sanitize_text(v, 1000, "ai_summary")

    @field_validator("ai_category")
    @classmethod
    def validate_category(cls, v):
        return sanitize_text(v, 128, "ai_category")

    @field_validator("inactivity_threshold")
    @classmethod
    def validate_threshold(cls, v):
        if v is not None and (v < 30 or v > 86400):
            raise ValueError("inactivity_threshold must be between 30 and 86400 seconds.")
        return v


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
    details: Optional[str] = None

    @field_validator("details")
    @classmethod
    def validate_details(cls, v):
        return sanitize_text(v, MAX_DETAILS_LEN, "details")


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

    @field_validator("default_inactivity_threshold")
    @classmethod
    def validate_threshold(cls, v):
        if v is not None and (v < 30 or v > 86400):
            raise ValueError("Threshold must be between 30 and 86400 seconds.")
        return v


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


# ── Search Schema ──────────────────────────────────────────────────────────────

class SearchQuery(BaseModel):
    q: str

    @field_validator("q")
    @classmethod
    def validate_query(cls, v):
        result = sanitize_text(v, MAX_SEARCH_LEN, "search query")
        if not result:
            raise ValueError("Search query cannot be empty.")
        return result
