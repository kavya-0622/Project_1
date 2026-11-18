from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import current_user
from app.models import User, Finding, AuditLog
from app.schemas import FindingIn, FindingOut, DecisionIn

router = APIRouter(prefix="/findings", tags=["findings"])

@router.get("", response_model=list[FindingOut])
def list_findings(status: str = "", db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = db.query(Finding).filter(Finding.workspace_id == user.workspace_id)
    if status: query = query.filter(Finding.status == status)
    return query.order_by(Finding.created_at.desc()).all()

@router.post("", response_model=FindingOut, status_code=201)
def create_finding(data: FindingIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = Finding(workspace_id=user.workspace_id, **data.model_dump())
    db.add(item); db.flush()
    db.add(AuditLog(workspace_id=user.workspace_id, user_id=user.id, action="finding.created",
                    entity_type="finding", entity_id=str(item.id), details=item.title))
    db.commit(); db.refresh(item)
    return item

@router.post("/{finding_id}/decision", response_model=FindingOut)
def decide(finding_id: int, data: DecisionIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if user.role not in ("owner", "finance_admin"):
        raise HTTPException(403, "Only workspace owners or finance admins can decide findings")
    if data.decision not in ("approved", "rejected"):
        raise HTTPException(400, "Decision must be approved or rejected")
    item = db.query(Finding).filter(Finding.id == finding_id, Finding.workspace_id == user.workspace_id).first()
    if not item: raise HTTPException(404, "Finding not found")
    item.status = data.decision
    db.add(AuditLog(workspace_id=user.workspace_id, user_id=user.id, action=f"finding.{data.decision}",
                    entity_type="finding", entity_id=str(item.id), details=data.note))
    db.commit(); db.refresh(item)
    return item
