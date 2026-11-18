from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import current_user
from app.models import User, Customer, AuditLog
from app.schemas import CustomerIn, CustomerOut

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("", response_model=list[CustomerOut])
def list_customers(q: str = "", db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = db.query(Customer).filter(Customer.workspace_id == user.workspace_id)
    if q:
        query = query.filter(Customer.name.ilike(f"%{q}%"))
    return query.order_by(Customer.name).all()

@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = Customer(workspace_id=user.workspace_id, **data.model_dump())
    db.add(item); db.flush()
    db.add(AuditLog(workspace_id=user.workspace_id, user_id=user.id, action="customer.created",
                    entity_type="customer", entity_id=str(item.id), details=item.name))
    db.commit(); db.refresh(item)
    return item

@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.query(Customer).filter(Customer.id == customer_id, Customer.workspace_id == user.workspace_id).first()
    if not item: raise HTTPException(404, "Customer not found")
    db.delete(item); db.commit()
