# Tech Stack — Skills Data Service

The Skills Data Service is a FastAPI service that returns **aggregate-only** skill-gap evidence for a population. It gets the evidence from a tenant-approved TechWolf API and normalizes it into internal evidence records.

- **Endpoint:** `POST /v1/skills/evidence`
- **Guardrails:** requests with `aggregate_only != true` are rejected with `403`. Minimum population coverage (default `0.65`), freshness window (default `30` days) and `max_results` (1–100) are enforced through the request `options`.
- **Failure mapping:** TechWolf timeout returns `504`. An unconfigured tenant adapter returns `501`.

## Stack

| Layer | Tool | Installed version | Notes |
|---|---|---|---|
| Language | Python | 3.12.3 | Uses the stdlib `typing` and `datetime` modules |
| Web framework | FastAPI | 0.141.1 | Routes, dependency injection (`Depends`), `HTTPException` |
| Data models / validation | Pydantic v2 | 2.13.5 | Request/response models, `Field` constraints |
| ASGI server | Uvicorn (`[standard]`) | 0.54.0 | Serves the FastAPI `app` |
| MCP | `mcp[cli]` (official Python SDK / FastMCP) | 2.2.0 | Model Context Protocol server + `mcp` CLI |
| FastAPI → MCP bridge | `fastapi-mcp` | 0.4.0 | Exposes FastAPI endpoints as MCP tools |
| Containerization | Docker Engine + Compose | 29.7.2 / v5.5.0 | System install. Builds the image from `Dockerfile` |
| Docker from Python | `docker` (Docker SDK) | 7.2.0 | Python client for the local Docker daemon |
| Testing | pytest | 9.1.1 | `tests/test_*.py` |
| Test client | httpx | 0.28.1 | Required by FastAPI's `TestClient` |
| External data source | TechWolf API | — | Tenant-approved contract, accessed through `techwolf_client.py` |
| Packaging | `pyproject.toml` | — | Project metadata / build config |

`requirements.txt` holds the pip-installable tools. Docker Engine and the TechWolf API are not pip packages.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Codebase Structure

```
skills-data-service/
├── app/
│   ├── main.py              # FastAPI routes
│   ├── models.py            # Pydantic request/response models
│   ├── techwolf_client.py   # Tenant-specific TechWolf adapter
│   ├── normalization.py     # TechWolf -> internal evidence record
│   ├── validation.py        # Coverage/freshness/privacy rules
│   ├── authorization.py     # Service identity + scopes
│   ├── audit.py             # Audit/correlation logging
│   ├── config.py            # Thresholds and environment config
│   └── errors.py            # Standard exception mapping
├── tests/
│   ├── test_contract.py
│   ├── test_validation.py
│   ├── test_authorization.py
│   ├── test_normalization.py
│   └── test_failure_modes.py
├── Dockerfile
├── pyproject.toml
└── README.md
```
