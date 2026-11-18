from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.api.deps import current_user
from app.models import User, Finding, Customer

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Finding).filter(Finding.workspace_id == user.workspace_id).all()
    total = sum(x.amount for x in rows if x.status not in ("rejected",))
    approved = sum(x.amount for x in rows if x.status == "approved")
    under_review = sum(x.amount for x in rows if x.status == "under_review")
    customers = db.query(func.count(Customer.id)).filter(Customer.workspace_id == user.workspace_id).scalar() or 0
    return {"potential_recovery": total, "approved_recovery": approved, "under_review": under_review,
            "open_findings": sum(x.status == "under_review" for x in rows), "customers_monitored": customers,
            "recovery_rate": round((approved / total * 100), 1) if total else 0,
            "monthly_trend": [{"month": "Jan", "value": 32000}, {"month": "Feb", "value": 41000},
                              {"month": "Mar", "value": 36500}, {"month": "Apr", "value": 52000},
                              {"month": "May", "value": 48000}, {"month": "Jun", "value": 59400}]}
