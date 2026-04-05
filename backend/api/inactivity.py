from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Tab, TabStatus
from schemas.tab import InactiveTabResponse, TabResponse
from services.notifier import notifier_service
from core.config import settings

router = APIRouter(prefix="/inactivity", tags=["Inactivity"])


@router.get("/check", response_model=list[InactiveTabResponse])
def check_inactive_tabs(db: Session = Depends(get_db)):
    """
    Scan all active tabs and return those that have exceeded their inactivity threshold.
    Does NOT auto-close — that is triggered separately via /inactivity/process.
    """
    active_tabs = db.query(Tab).filter(Tab.status == TabStatus.active).all()
    inactive = []

    for tab in active_tabs:
        last_active = tab.last_active_at
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=timezone.utc)

        inactive_seconds = (datetime.now(timezone.utc) - last_active).total_seconds()
        threshold = tab.inactivity_threshold or settings.DEFAULT_INACTIVITY_THRESHOLD

        if inactive_seconds > threshold:
            inactive.append(InactiveTabResponse(
                tab=tab,
                inactive_for_seconds=inactive_seconds,
                will_auto_close=tab.auto_close_enabled,
            ))

    return inactive


@router.post("/process", response_model=list[TabResponse])
def process_inactive_tabs(db: Session = Depends(get_db)):
    """
    For each inactive tab:
    - Mark it as inactive and record a reminder notification event.
    - If auto_close is enabled, mark it as auto_closed.

    The Electron frontend polls this endpoint (or uses the /check endpoint
    alongside WebSocket push) to trigger desktop notifications.
    """
    active_tabs = db.query(Tab).filter(Tab.status == TabStatus.active).all()
    updated_tabs = []

    for tab in active_tabs:
        last_active = tab.last_active_at
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=timezone.utc)

        inactive_seconds = (datetime.now(timezone.utc) - last_active).total_seconds()
        threshold = tab.inactivity_threshold or settings.DEFAULT_INACTIVITY_THRESHOLD

        if inactive_seconds > threshold:
            if tab.auto_close_enabled:
                tab.status = TabStatus.auto_closed
                tab.closed_at = datetime.now(timezone.utc)
                notifier_service.record_auto_close(db, tab)
            else:
                tab.status = TabStatus.inactive
                notifier_service.record_inactivity_reminder(db, tab, inactive_seconds)

            updated_tabs.append(tab)

    db.commit()
    for tab in updated_tabs:
        db.refresh(tab)

    return updated_tabs
