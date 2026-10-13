"""Security and integration regression coverage for the rule-evaluation services."""
import math

import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from grant_match_ai.models import FrontierPayload


def test_audit_hmac_detects_metadata_tampering():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("supervisor", "worker", "EVENT", {"status": "NOMINAL"})
    trail.log("supervisor", "worker", "EVENT", {"status": "ELEVATED"})
    assert trail.verify_integrity()

    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "forged"
    assert trail.verify_integrity(), "Returned snapshots must not mutate the ledger"

    trail.logs[0]["actor"] = "forged"
    assert not trail.verify_integrity(), "Every block signature must be checked"


def test_audit_hmac_detects_signature_tampering():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("supervisor", "worker", "EVENT", {"status": "NOMINAL"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert not trail.verify_integrity()


def test_nested_payload_identifier_is_rejected():
    supervisor = SystemSupervisor()
    payload = SystemTaskPayload(
        task_id="T1", target_identifier="KEY-1", primary_metric=1.0,
        attributes={"nested": {"contact": "jane@example.com"}},
    )
    with pytest.raises(SecurityException):
        supervisor.process_task(payload)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf, "invalid"])
def test_frontier_payload_finite_validation(bad):
    with pytest.raises(ValueError):
        FrontierPayload("T1", "KEY", bad, 1.0, "NOMINAL")


def test_audit_log_endpoint_restricted(monkeypatch):
    client = TestClient(app)
    monkeypatch.delenv("AUDIT_API_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 503
    monkeypatch.setenv("AUDIT_API_TOKEN", "integration-test-token")
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "wrong"}).status_code == 403
    response = client.get("/api/audit/logs", headers={"X-Audit-Token": "integration-test-token"})
    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_api_rejects_nested_personal_identifier():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T1", "target_identifier": "KEY", "primary_metric": 1.0,
        "attributes": {"note": "MRN 12345678"},
    })
    assert response.status_code == 422
    assert "MRN" not in response.text


def test_web_app_is_served_and_labels_are_present():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Local browser demo" in response.text
    assert 'for="task_id"' in response.text



def test_main_csv_export_quotes_spreadsheet_formulas(tmp_path):
    import csv
    from cli import main

    source = tmp_path / "input.csv"
    destination = tmp_path / "output.csv"
    source.write_text(
        'task_id,target_identifier,primary_metric,secondary_metric,status_descriptor\n'
        '"=HYPERLINK(""https://example.org"")",KEY-01,10,5,NOMINAL\n',
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(source), "-o", str(destination)]) == 0
    with destination.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["task_id"].startswith("'=HYPERLINK")
    assert rows[0]["overall_urgency"] == "ROUTINE"


def test_invalid_simulation_size_rejected():
    from simulator import run_simulation

    with pytest.raises(ValueError, match="positive"):
        run_simulation(0)
