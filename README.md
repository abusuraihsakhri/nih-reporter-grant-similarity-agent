# Nih Reporter Grant Similarity Agent

> **Domain:** Clinical Decision Support & Biomedical Computing / Research Administration

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Nih Reporter Grant Similarity Agent is a multi-agent evaluation engine that processes task payloads through specialized workers to produce consensus dossiers with cryptographic audit trails. It supports:

- **Multi-agent evaluation** with InvariantQC, Safety Escalation, and Protocol Conformance workers
- **HMAC-SHA256 tamper-evident audit logging** with chained integrity verification
- **Zero-PHI outbound guard** that blocks SSNs, MRNs, emails, and patient identifiers
- **FastAPI REST API** for task processing and chat queries
- **CLI interface** for single evaluations, batch CSV processing, and server mode
- **Prometheus metrics export** and WebSocket telemetry streaming

---

## ⚙️ Architecture

The project consists of two main modules:

| Module | Description |
|--------|-------------|
| `agents/` | Core evaluation engine with supervisor, workers, PHI guard, and audit trail |
| `grant_match_ai/` | Frontier domain module for NIH RePORT & RePADD grant similarity analysis |
| `enrichment/` | Enrichment suite with portfolio, compliance, budget, and collaboration modules |

---

## 💻 Quickstart

### Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

### CLI Usage

#### Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

#### Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

#### Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

#### Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

#### Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Entity or target key | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary confidence score | Optional (default: 0.0) |
| `is_critical_flag` | Emergency escalation flag | Optional (default: False) |
| `status_descriptor` | Status code or phenotype | Optional (default: "NOMINAL") |

---

## 🛡️ Security

- **Zero-PHI Outbound Guard:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
- **Input Validation:** Finite numeric checks, string length limits, and NaN/Infinity rejection
- **Audit Secret Key:** Configure via `AUDIT_SECRET_KEY` environment variable (required for production)

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | HMAC signing key for audit trail | Ephemeral (generated per session) |
| `MODEL_PROVIDER` | LLM backend (mock, ollama, claude, openai) | mock |

---

## 🧪 Testing

Run the full test suite:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --cov=agents --cov=grant_match_ai --cov-report=term-missing
```

Execute high-throughput simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t nih-reporter-grant-similarity-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key nih-reporter-grant-similarity-agent
```

Or using docker-compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
nih-reporter-grant-similarity-agent/
├── agents/                  # Core evaluation engine
│   ├── __init__.py
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # PHI guard, audit trail, security
│   ├── learning.py         # Active learning calibration
│   ├── llm_factory.py      # LLM client factory
│   ├── metrics.py          # Prometheus metrics collector
│   ├── models.py           # Pydantic data models
│   ├── streamer.py         # WebSocket telemetry
│   ├── supervisor.py       # Multi-agent orchestrator
│   └── workers.py          # Specialized evaluation workers
├── grant_match_ai/          # Grant similarity module
│   ├── agents.py           # Domain-specific agents
│   ├── cli.py              # CLI for grant module
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Domain data models
│   └── server.py           # FastAPI server factory
├── tests/                   # Test suite
│   ├── conftest.py         # Pytest configuration
│   ├── test_enrichment.py
│   ├── test_grant_match_ai.py
│   └── test_nih_reporter_grant_similarity_agent.py
├── web/index.html           # Operations console UI
├── enrichment.py            # Feature enrichment suite
├── cli.py                   # Main CLI entry point
├── simulator.py             # High-throughput stress testing
├── pyproject.toml           # Project configuration
├── Dockerfile               # Container build
└── docker-compose.yml       # Compose configuration
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
