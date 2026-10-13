# NIH RePORTER Grant Similarity Agent

A Python rule-evaluation prototype with a CLI, FastAPI service, and self-contained browser demonstration.

**Scope:** The current code evaluates numeric thresholds, a critical flag, and anomaly keywords. Despite the repository name, it **does not** query NIH RePORTER, compare grant abstracts, compute cosine similarity, predict NIH study sections, or establish scientific overlap. The outputs are rule alerts, not validated research or clinical recommendations.

## Features

- Three rule workers: primary metric greater than 25, secondary metric greater than 12 or critical flag, and anomaly-descriptor detection.
- Consensus dossier with routine, elevated, or critical severity.
- In-memory HMAC-SHA256 audit chain for the main Python engine, including signature verification.
- Python CLI, CSV batch processor, JSON API, and independent `grant_match_ai` compatibility interface.
- `web/index.html`: API console when served from the backend; clearly labeled local demonstration when opened from a file or GitHub Pages.

## Run locally

Requires Python 3.9 or newer. CI currently tests Python 3.10–3.12.

```bash
python -m pip install -e ".[api,dev]"
python -m pytest -q
nih-reporter-grant-similarity-agent audit --task-id TEST-01 --target KEY-01 --primary 28 --secondary 14
nih-reporter-grant-similarity-agent batch -i sample.csv -o results.csv
nih-reporter-grant-similarity-agent verify-audit
nih-reporter-grant-similarity-agent serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the console or `http://127.0.0.1:8000/docs` for generated API documentation. The original compatibility entry point `nih-reporter-grant-similarity-engine` remains available and invokes `grant_match_ai.cli`.

### API

- `GET /health` — status and service metadata.
- `POST /api/audit` — rule evaluation; requires `task_id`, `target_identifier`, and `primary_metric`. Other fields are optional.
- `POST /api/chat` — deterministic mock supervisory response (not a live language model).
- `GET /metrics` — JSON counters, not Prometheus text.
- `GET /api/audit/logs` — audit metadata, restricted by the `X-Audit-Token` header. Requires a non-empty `AUDIT_API_TOKEN` on the server; otherwise returns HTTP 503.

The `grant_match_ai` directory exposes a second, separately defined threshold-based interface (`python -m grant_match_ai.cli --help`). Its labels describe grant-related agents, but its calculations are not a grant-similarity algorithm.

## Docker

Create a local `.env` using `.env.example`. Set **distinct, random, non-empty** values for `AUDIT_SECRET_KEY` and `AUDIT_API_TOKEN`, then run:

```bash
docker compose up --build
```

Compose binds the HTTP service to `127.0.0.1:8000`, not the public network. Do not expose the API directly to untrusted clients; audit and evaluation endpoints are not a complete access-control system. A reverse proxy with authentication and TLS is required for a public deployment.

## Browser and GitHub Pages

`web/index.html` is a static, responsive client requiring no JavaScript build or Python runtime. From a local file or GitHub Pages, it executes the same three **illustrative threshold rules** in JavaScript. It does not sign an audit record, contact NIH, or send data to a backend. When served from the FastAPI root route, it calls the same-origin API instead. The UI does not silently fabricate signed audit results when a server request fails.

GitHub Pages can host only the static demonstration; it cannot run the Python FastAPI service, maintain the Python audit ledger, or store signing secrets. No Pyodide runtime is necessary for the three simple local rules.

## Security and data handling

- The in-memory audit ledger signs each block with HMAC-SHA256 and verifies block signatures and links. It **does not persist** across restarts, and its confidentiality depends on protecting the signing key.
- A regex-based identifier guard checks several common PHI patterns in input. It is **not comprehensive de-identification or a HIPAA compliance guarantee**. Do not submit protected health information or other identifiable personal data.
- API evaluation data and logs reside in process memory. The browser demonstration runs locally without uploading input.
- Keep `.env` and credentials out of version control. Container Compose requires explicit credentials.

## Development and tests

```bash
python -m pip install -e ".[api,dev]"
python -m compileall -q agents grant_match_ai cli.py enrichment.py simulator.py
python -m pytest -q
```

CI also checks package installation, JavaScript syntax, and the packaged CLI command. The implementation uses Python, Pydantic, FastAPI/Uvicorn (optional API extras), HTML, CSS, and vanilla JavaScript.

## License

MIT — see [LICENSE](LICENSE).
