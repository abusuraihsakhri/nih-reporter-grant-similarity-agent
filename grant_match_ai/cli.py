"""
Command-Line Interface for GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent.
"""
import argparse
import csv
import json
import sys
from agents.base import SecurityException
from .models import FrontierPayload
from .agents import GrantMatchCoordinator

coordinator = GrantMatchCoordinator()


def _safe_spreadsheet_cell(value):
    """Neutralize spreadsheet formulas in exported CSVs without changing numbers."""
    if not isinstance(value, str):
        return value
    if value.lstrip().startswith(("=", "+", "-", "@")):
        try:
            float(value)
        except ValueError:
            return "'" + value
    return value



def main(argv=None):
    parser = argparse.ArgumentParser(prog="nih-reporter-grant-similarity-agent", description="GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run single task evaluation")
    p_audit.add_argument("--task-id", default="TASK-2026-001")
    p_audit.add_argument("--target", default="TARGET-GEN-01")
    p_audit.add_argument("--primary", type=float, default=29.4)
    p_audit.add_argument("--secondary", type=float, default=15.1)
    p_audit.add_argument("--critical", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")

    # Chat
    p_chat = subparsers.add_parser("chat", help="System configuration query")
    p_chat.add_argument("query", nargs="+")

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "audit":
        payload = FrontierPayload(
            task_id=args.task_id,
            target_identifier=args.target,
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_descriptor=args.status,
            is_critical_flag=args.critical,
        )
        dossier = coordinator.process(payload)
        print("=" * 80)
        print(f"  GRANTMATCH-AI: NIH REPORT & REPADD GRANT SCIENTIFIC SIMILARITY AGENT")
        print(f"  Domain: Research Administration | Standard: NIH RePORT & Center for Scientific Review")
        print(f"  Task: {dossier['task_id']} | Status: [{dossier['overall_status']}] | Total Alerts: {dossier['total_alerts']}")
        print("=" * 80)
        for a in dossier["alerts"]:
            print(f"\n  [{a['status']}] from {a['origin_agent']}:")
            print(f"  Summary: {a['summary']}")
            print(f"  Details: {a['technical_details']}")
            print(f"  Action:  {a['actionable_remediation']}")
        print("\n" + "=" * 80)
        return 0

    if args.command == "chat":
        ans = coordinator.query_supervisory_chat(" ".join(args.query))
        print(f"\n[GrantMatchCoordinator]:\n{ans}\n")
        return 0

    if args.command == "batch":
        with open(args.input, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

        out_fields = list(dict.fromkeys(fieldnames + ["overall_status", "total_alerts", "critical_count", "consensus_summary"]))
        out_rows = []
        errors = 0
        for idx, r in enumerate(rows, start=1):
            try:
                payload = FrontierPayload(
                    task_id=r.get("task_id", f"TASK-{idx:03d}"),
                    target_identifier=r.get("target_identifier", f"TARGET-{idx:03d}"),
                    primary_metric=float(r.get("primary_metric", 15.0)),
                    secondary_metric=float(r.get("secondary_metric", 5.0)),
                    status_descriptor=r.get("status_descriptor", "NOMINAL"),
                    is_critical_flag=str(r.get("is_critical_flag", "")).lower() in ("true", "1", "yes"),
                )
                dossier = coordinator.process(payload)
                row_dict = dict(r)
                row_dict["overall_status"] = dossier["overall_status"]
                row_dict["total_alerts"] = dossier["total_alerts"]
                row_dict["critical_count"] = dossier["critical_count"]
                row_dict["consensus_summary"] = dossier["consensus_summary"]
                out_rows.append(row_dict)
            except (ValueError, TypeError, SecurityException) as e:
                errors += 1
                print(f"  [WARN] Row {idx} skipped: {e}")

        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([_safe_spreadsheet_cell(name) for name in out_fields])
            for row in out_rows:
                writer.writerow([_safe_spreadsheet_cell(row.get(name, "")) for name in out_fields])
        print(f"Processed {len(out_rows)} records -> {args.output} ({errors} skipped)")
        return 0

    if args.command == "serve":
        try:
            import uvicorn
            from .server import create_app
            app = create_app()
            if app:
                print(f"Starting GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent on http://{args.host}:{args.port}")
                uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            print("FastAPI / uvicorn not installed. Run 'pip install fastapi uvicorn'")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
