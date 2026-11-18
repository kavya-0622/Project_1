from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models import User, Workspace, Customer, Finding, AuditLog
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(409, "An account with this email already exists")
    workspace = Workspace(name=data.workspace_name)
    db.add(workspace)
    db.flush()
    user = User(workspace_id=workspace.id, name=data.name, email=data.email.lower(),
                password_hash=hash_password(data.password), role="owner")
    db.add(user)
    db.flush()
    samples = [
        ("Northstar Logistics", "Usage exceeds contracted tier", "Usage variance", 28400, .96, "Active seats: 1,240 · Contracted seats: 1,000"),
        ("Asteron Health", "Unbilled implementation services", "Unbilled services", 18600, .91, "Signed SOW includes 3 delivery milestones"),
        ("Vertex Systems", "Renewal uplift not applied", "Contract pricing", 12350, .88, "Renewal schedule indicates 7.5% uplift"),
    ]
    for customer, title, category, amount, confidence, evidence in samples:
        db.add(Finding(workspace_id=workspace.id, customer_name=customer, title=title,
                       category=category, description="Potential revenue variance detected. Validate source records before action.",
                       amount=amount, confidence=confidence, evidence=evidence))
    db.add(AuditLog(workspace_id=workspace.id, user_id=user.id, action="workspace.created",
                    entity_type="workspace", entity_id=str(workspace.id), details="Initial workspace registration"))
    db.commit()
    return TokenOut(access_token=create_access_token(str(user.id)), user=UserOut.model_validate(user))

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return TokenOut(access_token=create_access_token(str(user.id)), user=UserOut.model_validate(user))

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
