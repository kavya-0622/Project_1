from celery import Celery
from app.core.config import settings

celery = Celery("revora", broker=settings.redis_url, backend=settings.redis_url)

@celery.task
def run_reconciliation(workspace_id: int):
    # Integrate approved source connectors here. Persist evidence and candidate findings;
    # never alter customer invoices or trigger collections automatically.
    return {"workspace_id": workspace_id, "status": "queued_scaffold"}
