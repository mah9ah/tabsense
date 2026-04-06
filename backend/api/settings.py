from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from core.security import limiter, LIMITS
from db.database import get_db
from db.models import UserSettings
from schemas.tab import UserSettingsUpdate, UserSettingsResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


def _get_or_create_settings(db: Session) -> UserSettings:
    s = db.query(UserSettings).filter(UserSettings.id == 1).first()
    if not s:
        s = UserSettings(id=1)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


@router.get("/", response_model=UserSettingsResponse)
@limiter.limit(LIMITS["default"])
def get_settings(request: Request, db: Session = Depends(get_db)):
    return _get_or_create_settings(db)


@router.patch("/", response_model=UserSettingsResponse)
@limiter.limit(LIMITS["write"])
def update_settings(request: Request, payload: UserSettingsUpdate, db: Session = Depends(get_db)):
    s = _get_or_create_settings(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    s.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(s)
    return s
