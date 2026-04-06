from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    Float, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
import enum

from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    display_name = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TabType(str, enum.Enum):
    browser_tab = "browser_tab"
    desktop_app = "desktop_app"


class TabStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    auto_closed = "auto_closed"
    manually_closed = "manually_closed"


class EventType(str, enum.Enum):
    opened = "opened"
    activated = "activated"
    deactivated = "deactivated"
    inactivity_reminder = "inactivity_reminder"
    auto_closed = "auto_closed"
    manually_closed = "manually_closed"
    summary_generated = "summary_generated"


class Tab(Base):
    __tablename__ = "tabs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TabType), nullable=False)           # browser_tab | desktop_app

    # Identity
    title = Column(String(512), nullable=False)
    url = Column(String(2048), nullable=True)              # Null for desktop apps
    app_name = Column(String(256), nullable=True)          # Null for browser tabs
    favicon_url = Column(String(2048), nullable=True)

    # Timestamps
    opened_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime, nullable=True)

    # Status
    status = Column(Enum(TabStatus), default=TabStatus.active)

    # AI
    ai_summary = Column(Text, nullable=True)
    ai_category = Column(String(128), nullable=True)

    # User settings per tab
    inactivity_threshold = Column(Integer, nullable=True)  # Seconds; null = use global default
    auto_close_enabled = Column(Boolean, default=False)

    # Relationships
    events = relationship("Event", back_populates="tab", cascade="all, delete-orphan")

    def is_inactive(self, threshold_seconds: int) -> bool:
        effective_threshold = self.inactivity_threshold or threshold_seconds
        now = datetime.now(timezone.utc)
        last_active = self.last_active_at
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=timezone.utc)
        return (now - last_active).total_seconds() > effective_threshold


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    tab_id = Column(Integer, ForeignKey("tabs.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(EventType), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    details = Column(Text, nullable=True)  # JSON string for extra context

    tab = relationship("Tab", back_populates="events")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, default=1)  # Single-row settings table
    default_inactivity_threshold = Column(Integer, default=1800)  # 30 min
    auto_close_enabled_globally = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    ai_summaries_enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
