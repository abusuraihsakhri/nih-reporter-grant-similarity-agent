"""
FastAPI REST API Server for GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from agents.base import SecurityException
from .agents import GrantMatchCoordinator

coordinator = GrantMatchCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field
        from fastapi import HTTPException

        app = FastAPI(
            title="GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent",
            description="Evaluates threshold and anomaly rules; does not compute grant text similarity.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = "TASK-2026-001"
            target_identifier: str = "TARGET-BIO-KEY"
            primary_metric: float = 28.5
            secondary_metric: float = 14.2
            status_descriptor: str = "DISCORDANT_ANOMALY"
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = Field(default_factory=dict)

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "nih-reporter-grant-similarity-agent", "domain": "Research Administration", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            try:
                payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
                )
                return coordinator.process(payload)
            except SecurityException:
                raise HTTPException(status_code=422, detail="Input contains a possible personal identifier") from None
            except (ValueError, TypeError):
                raise HTTPException(status_code=422, detail="Metrics must be finite numbers") from None

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
