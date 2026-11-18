from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import current_user
from app.models import User, AuditLog

router = APIRouter(prefix="/audit-logs", tags=["audit"])

@router.get("")
def list_logs(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(AuditLog).filter(AuditLog.workspace_id == user.workspace_id).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [{"id": r.id, "action": r.action, "entity_type": r.entity_type, "entity_id": r.entity_id,
             "details": r.details, "created_at": r.created_at} for r in rows]
