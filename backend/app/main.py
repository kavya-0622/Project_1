from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import Base, engine
from app.models import Workspace, User, Customer, Finding, AuditLog
from app.api.routes import auth, dashboard, customers, findings, audit

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Revora API", version="1.0.0", description="Revenue leakage detection and recovery workflow API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
for router in (auth.router, dashboard.router, customers.router, findings.router, audit.router):
    app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "service": "revora-api"}
