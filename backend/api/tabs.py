import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Tab, Event, EventType, TabStatus
from schemas.tab import TabCreate, TabUpdate, TabResponse, EventResponse

router = APIRouter(prefix="/tabs", tags=["Tabs"])


@router.post("/", response_model=TabResponse, status_code=201)
def create_tab(payload: TabCreate, db: Session = Depends(get_db)):
    """Register a newly opened tab or app."""
    tab = Tab(**payload.model_dump())
    db.add(tab)
    db.flush()  # Get the ID before committing

    event = Event(tab_id=tab.id, type=EventType.opened)
    db.add(event)
    db.commit()
    db.refresh(tab)
    return tab


@router.get("/", response_model=list[TabResponse])
def list_tabs(
    status: Optional[TabStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by title, URL, or AI summary"),
    db: Session = Depends(get_db),
):
    """List all tabs, with optional status filter and full-text search."""
    query = db.query(Tab)

    if status:
        query = query.filter(Tab.status == status)

    if search:
        term = f"%{search}%"
        query = query.filter(
            Tab.title.ilike(term)
            | Tab.url.ilike(term)
            | Tab.ai_summary.ilike(term)
            | Tab.app_name.ilike(term)
            | Tab.ai_category.ilike(term)
        )

    return query.order_by(Tab.last_active_at.desc()).all()


@router.get("/{tab_id}", response_model=TabResponse)
def get_tab(tab_id: int, db: Session = Depends(get_db)):
    tab = db.query(Tab).filter(Tab.id == tab_id).first()
    if not tab:
        raise HTTPException(status_code=404, detail="Tab not found")
    return tab


@router.patch("/{tab_id}", response_model=TabResponse)
def update_tab(tab_id: int, payload: TabUpdate, db: Session = Depends(get_db)):
    """Update tab metadata, settings, or activity timestamp."""
    tab = db.query(Tab).filter(Tab.id == tab_id).first()
    if not tab:
        raise HTTPException(status_code=404, detail="Tab not found")

    update_data = payload.model_dump(exclude_unset=True)

    # Record activation event if last_active_at is being updated
    if "last_active_at" in update_data:
        db.add(Event(tab_id=tab.id, type=EventType.activated))
        if tab.status == TabStatus.inactive:
            update_data["status"] = TabStatus.active

    for field, value in update_data.items():
        setattr(tab, field, value)

    db.commit()
    db.refresh(tab)
    return tab


@router.post("/{tab_id}/close", response_model=TabResponse)
def close_tab(
    tab_id: int,
    auto: bool = Query(False, description="True if closed by auto-close logic"),
    db: Session = Depends(get_db),
):
    """Mark a tab as closed."""
    tab = db.query(Tab).filter(Tab.id == tab_id).first()
    if not tab:
        raise HTTPException(status_code=404, detail="Tab not found")

    tab.status = TabStatus.auto_closed if auto else TabStatus.manually_closed
    tab.closed_at = datetime.now(timezone.utc)

    event_type = EventType.auto_closed if auto else EventType.manually_closed
    db.add(Event(tab_id=tab.id, type=event_type))

    db.commit()
    db.refresh(tab)
    return tab


@router.delete("/{tab_id}", status_code=204)
def delete_tab(tab_id: int, db: Session = Depends(get_db)):
    """Permanently remove a tab and its events from the database."""
    tab = db.query(Tab).filter(Tab.id == tab_id).first()
    if not tab:
        raise HTTPException(status_code=404, detail="Tab not found")
    db.delete(tab)
    db.commit()


@router.get("/{tab_id}/events", response_model=list[EventResponse])
def get_tab_events(tab_id: int, db: Session = Depends(get_db)):
    """Get full event history for a tab."""
    tab = db.query(Tab).filter(Tab.id == tab_id).first()
    if not tab:
        raise HTTPException(status_code=404, detail="Tab not found")
    return tab.events
