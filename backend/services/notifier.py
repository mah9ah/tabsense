import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from db.models import Tab, Event, EventType

logger = logging.getLogger(__name__)


class NotifierService:
    """
    Handles notification logic. The actual desktop notification is sent
    by the Electron frontend via WebSocket or polling. This service records
    notification events and prepares the payload the frontend will display.
    """

    def build_inactivity_payload(self, tab: Tab, inactive_seconds: float) -> dict:
        minutes = int(inactive_seconds // 60)
        name = tab.title or tab.app_name or "Unknown"
        return {
            "type": "inactivity_reminder",
            "tab_id": tab.id,
            "title": f"Still using {name}?",
            "body": (
                f'"{name}" has been inactive for {minutes} minute(s). '
                + (tab.ai_summary or "No summary available.")
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def build_auto_close_payload(self, tab: Tab) -> dict:
        name = tab.title or tab.app_name or "Unknown"
        return {
            "type": "auto_closed",
            "tab_id": tab.id,
            "title": f"Auto-closed: {name}",
            "body": f'"{name}" was automatically closed due to inactivity.',
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def record_inactivity_reminder(self, db: Session, tab: Tab, inactive_seconds: float):
        payload = self.build_inactivity_payload(tab, inactive_seconds)
        event = Event(
            tab_id=tab.id,
            type=EventType.inactivity_reminder,
            details=json.dumps(payload),
        )
        db.add(event)
        db.commit()
        logger.info(f"[Notifier] Inactivity reminder recorded for tab_id={tab.id}")
        return payload

    def record_auto_close(self, db: Session, tab: Tab):
        payload = self.build_auto_close_payload(tab)
        event = Event(
            tab_id=tab.id,
            type=EventType.auto_closed,
            details=json.dumps(payload),
        )
        db.add(event)
        db.commit()
        logger.info(f"[Notifier] Auto-close event recorded for tab_id={tab.id}")
        return payload


notifier_service = NotifierService()
