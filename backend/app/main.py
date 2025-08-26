from fastapi import FastAPI

# import your routers
from backend.app.api import billing  # backend/app/api/billing.py
try:
    from backend.app.api import crm  # backend/app/api/crm.py (if you have it)
except ImportError:
    crm = None  # optional

app = FastAPI(title="Tourism API")

# mount routers
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])  # legacy
if crm is not None:
    app.include_router(crm.router, prefix="/api/crm", tags=["crm"])
    app.include_router(crm.router, prefix="/crm", tags=["crm"])  # legacy

# health check
@app.get("/api/health")
def health():
    return {"ok": True}
