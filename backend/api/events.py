from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Event, EventType
from schemas.tab import EventCreate, EventResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    """Manually log an event (e.g., from the Electron main process)."""
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=list[EventResponse])
def list_events(
    tab_id: Optional[int] = Query(None),
    type: Optional[EventType] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """List events with optional filters."""
    query = db.query(Event)
    if tab_id:
        query = query.filter(Event.tab_id == tab_id)
    if type:
        query = query.filter(Event.type == type)
    return query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
