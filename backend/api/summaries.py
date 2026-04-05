from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Tab, Event, EventType
from schemas.tab import SummaryRequest, SummaryResponse
from services.gemini import gemini_service

router = APIRouter(prefix="/summaries", tags=["AI Summaries"])


@router.post("/", response_model=SummaryResponse)
def generate_summary(payload: SummaryRequest, db: Session = Depends(get_db)):
    """
    Generate (or regenerate) an AI summary for a tab.
    Stores the result back on the Tab record.
    """
    tab = db.query(Tab).filter(Tab.id == payload.tab_id).first()
    if not tab:
        raise HTTPException(status_code=404, detail="Tab not found")

    result = gemini_service.summarize_tab(
        title=tab.title,
        url=tab.url,
        app_name=tab.app_name,
    )

    tab.ai_summary = result["summary"]
    tab.ai_category = result["category"]

    db.add(Event(
        tab_id=tab.id,
        type=EventType.summary_generated,
        details=f'{{"summary": "{result["summary"]}", "category": "{result["category"]}"}}'
    ))
    db.commit()
    db.refresh(tab)

    return SummaryResponse(
        tab_id=tab.id,
        summary=tab.ai_summary,
        category=tab.ai_category,
    )


@router.post("/batch", response_model=list[SummaryResponse])
def generate_summaries_for_all(db: Session = Depends(get_db)):
    """
    Generate AI summaries for all tabs that don't have one yet.
    Useful on first launch or after re-enabling AI summaries.
    """
    tabs_without_summary = db.query(Tab).filter(Tab.ai_summary.is_(None)).all()

    results = []
    for tab in tabs_without_summary:
        result = gemini_service.summarize_tab(
            title=tab.title,
            url=tab.url,
            app_name=tab.app_name,
        )
        tab.ai_summary = result["summary"]
        tab.ai_category = result["category"]
        db.add(Event(
            tab_id=tab.id,
            type=EventType.summary_generated,
            details=f'{{"summary": "{result["summary"]}", "category": "{result["category"]}"}}'
        ))
        results.append(SummaryResponse(
            tab_id=tab.id,
            summary=tab.ai_summary,
            category=tab.ai_category,
        ))

    db.commit()
    return results
