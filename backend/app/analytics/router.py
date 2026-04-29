from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.users import User
from app.models.applications import Application

router = APIRouter(prefix="/analytics", tags=["analytics"])

def detect_source(link: str | None) -> str:
    if not link:
        return "Direct"
    link = link.lower()
    if "linkedin" in link:   return "LinkedIn"
    if "indeed" in link:     return "Indeed"
    if "pnet" in link:       return "PNet"
    if "greenhouse" in link: return "Greenhouse"
    if "lever" in link:      return "Lever"
    if "executive" in link:  return "ExecutivePlacements"
    return "Other"

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    apps = db.query(Application).filter(
        Application.user_id == current_user.id
    ).all()

    total = len(apps)
    if total == 0:
        return {
            "total": 0,
            "response_rate": 0,
            "interview_rate": 0,
            "status_breakdown": {},
            "source_breakdown": {},
            "avg_days_to_response": None,
            "best_source": None,
        }

    # Status breakdown
    status_breakdown: dict[str, int] = {}
    for app in apps:
        status_breakdown[app.status] = status_breakdown.get(app.status, 0) + 1

    # Response rate — anything beyond Applied counts as a response
    responded = sum(1 for a in apps if a.status in {"Interview", "Offer", "Rejected"})
    response_rate = round(responded / total * 100) if total > 0 else 0

    # Interview rate
    interviewed = sum(1 for a in apps if a.status in {"Interview", "Offer"})
    interview_rate = round(interviewed / total * 100) if total > 0 else 0

    # Source breakdown
    source_breakdown: dict[str, dict] = {}
    for app in apps:
        source = detect_source(app.link)
        if source not in source_breakdown:
            source_breakdown[source] = {"total": 0, "interviews": 0, "offers": 0}
        source_breakdown[source]["total"] += 1
        if app.status in {"Interview", "Offer"}:
            source_breakdown[source]["interviews"] += 1
        if app.status == "Offer":
            source_breakdown[source]["offers"] += 1

    # Add response rate per source
    for source in source_breakdown:
        t = source_breakdown[source]["total"]
        i = source_breakdown[source]["interviews"]
        source_breakdown[source]["rate"] = round(i / t * 100) if t > 0 else 0

    # Best source by interview rate
    best_source = max(
        source_breakdown.items(),
        key=lambda x: x[1]["rate"],
        default=(None, {})
    )[0] if source_breakdown else None

    # Avg days to response — days between date_applied and first status change
    days_list = []
    for app in apps:
        if app.status in {"Interview", "Offer", "Rejected"}:
            if app.date_applied:
                delta = (date.today() - app.date_applied).days
                days_list.append(delta)

    avg_days = round(sum(days_list) / len(days_list)) if days_list else None

    return {
        "total": total,
        "response_rate": response_rate,
        "interview_rate": interview_rate,
        "status_breakdown": status_breakdown,
        "source_breakdown": source_breakdown,
        "avg_days_to_response": avg_days,
        "best_source": best_source,
    }