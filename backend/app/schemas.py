from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    workspace_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    workspace_id: int
    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class CustomerIn(BaseModel):
    name: str
    account_code: str = ""
    industry: str = ""
    annual_value: float = 0
    status: str = "active"

class CustomerOut(CustomerIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

class FindingIn(BaseModel):
    customer_name: str
    title: str
    category: str = "Billing variance"
    description: str = ""
    amount: float = Field(ge=0)
    confidence: float = Field(default=0.8, ge=0, le=1)
    evidence: str = ""

class DecisionIn(BaseModel):
    decision: str
    note: str = ""

class FindingOut(BaseModel):
    id: int
    customer_name: str
    title: str
    category: str
    description: str
    amount: float
    confidence: float
    status: str
    evidence: str
    model_config = ConfigDict(from_attributes=True)
