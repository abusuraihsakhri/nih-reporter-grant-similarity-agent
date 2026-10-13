"""
FastAPI REST API Server for Nih Reporter Grant Similarity Agent.
"""
import os
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Nih Reporter Grant Similarity Agent API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).resolve().parent.parent / "web" / "index.html")


def require_audit_token(x_audit_token: Optional[str] = Header(default=None)):
    """Do not expose log metadata without an explicitly configured credential."""
    expected = os.environ.get("AUDIT_API_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Audit log access is not configured")
    if not x_audit_token or not secrets.compare_digest(x_audit_token, expected):
        raise HTTPException(status_code=403, detail="Audit log access denied")


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "nih-reporter-grant-similarity-agent", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a possible personal identifier") from None
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Input contains a possible personal identifier") from None


@app.get("/api/audit/logs")
def api_audit_logs(_authorization: None = Depends(require_audit_token)):
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
