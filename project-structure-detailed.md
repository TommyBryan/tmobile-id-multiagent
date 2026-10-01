# Codebase Structure — What Each Part Does

This is the detailed version of `project-structure.md`. Same layout, but every file gets an
explanation of what belongs in it, what it talks to, and why it's split out on its own.

The things that come straight from the T-Mobile L&D architecture doc (the `POST /v1/skills/evidence`
route, the `Population` / `DiagnosticContext` / `Options` / `SkillEvidenceRequest` models, the
TechWolf data source) are called out by name. Anything described as "for example" is a suggestion
for how to fill the file in, not something the doc requires.

---

## The layout

```
skills-data-service/
├── app/
│   ├── main.py               # FastAPI routes
│   ├── models.py             # Pydantic request/response models
│   ├── techwolf_client.py    # Tenant-specific TechWolf adapter
│   ├── normalization.py      # TechWolf -> internal evidence record
│   ├── validation.py         # coverage/freshness/privacy rules
│   ├── authorization.py      # service identity + scopes
│   ├── audit.py              # audit/correlation logging
│   ├── config.py             # thresholds and environment config
│   └── errors.py             # standard exception mapping
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

**The big idea:** `main.py` is the front door. Every other file in `app/` does exactly one job, and
`main.py` calls them in order. That keeps each piece small enough to test on its own, and it means
when something breaks (TechWolf is down, a request is unauthorized, data is stale) you know which
file to open.

---

## `app/` — the service itself

### `main.py` — FastAPI routes
**What it is:** The entry point. It creates the FastAPI app and defines the HTTP endpoints.

**What goes in it:**
- `app = FastAPI(title="Skills Data Service", version="1.0.0")`
- The `POST /v1/skills/evidence` route
- Wiring for error handlers from `errors.py` and middleware from `audit.py`

**What it should *not* contain:** Business logic. A route function should read like a checklist:
check authorization → call TechWolf → normalize → validate → return. Each of those steps is a
function imported from another file.

**How it connects:** Uvicorn runs this file (`uvicorn app.main:app --reload`). It imports from
nearly every other file in `app/`.

**Analogy for you:** Like `app.py` in a Flask project — but with the logic pushed out into helper
modules instead of living inside the route.

---

### `models.py` — Pydantic request/response models
**What it is:** The definitions of what data coming into and going out of the API must look like.

**What goes in it:**
- The request models from the doc's scaffold: `Population`, `DiagnosticContext`, `Options`, and
  `SkillEvidenceRequest` (which is built out of the other three)
- The response model — the shape of the skill evidence you send back
- Optionally, the internal evidence record that `normalization.py` produces

**Why it's its own file:** Almost every other module needs these classes. Putting them in one place
means there's a single source of truth for "what does a request look like?" — and FastAPI uses these
same classes to auto-generate the OpenAPI spec.

**How it connects:** `main.py` uses them as route parameters/return types. `normalization.py` builds
them. `validation.py` inspects them. `test_contract.py` checks them.

---

### `techwolf_client.py` — Tenant-specific TechWolf adapter
**What it is:** The only file that knows how to talk to TechWolf (the external skills-data
provider).

**What goes in it:**
- Building the HTTP request to TechWolf's API (URL, headers, credentials pulled from `config.py`)
- Sending it and returning the raw response
- Timeouts and retry behavior
- Turning TechWolf-side failures (timeout, 500, bad credentials) into the service's own exceptions
  from `errors.py`

**What "tenant-specific" means:** TechWolf is configured per customer (per tenant). T-Mobile's
TechWolf setup — its endpoint, credentials, field names — lives here, not scattered through the
codebase.

**What "adapter" means:** It hides TechWolf's details from the rest of the app. If TechWolf changes
their API, or you swap to a different provider, this is the only file (plus `normalization.py`)
that should need to change.

**How it connects:** Called by `main.py`. Hands its raw output to `normalization.py`.

---

### `normalization.py` — TechWolf → internal evidence record
**What it is:** A translator. It takes TechWolf's raw response and converts it into *your* format.

**What goes in it:**
- Functions that map TechWolf's field names and structure onto your internal evidence record
- Cleanup like consistent casing, date formats, and dropping fields you don't use

**Why it matters:** The rest of the system (other agents, the analytics side, the canonical objects
like the Skill Gap Evidence Record) should never have to understand TechWolf's format. They only see
your normalized record. This is what keeps the vendor swappable.

**How it connects:** Receives data from `techwolf_client.py`, produces models defined in
`models.py`, passes the result on to `validation.py`.

---

### `validation.py` — Coverage / freshness / privacy rules
**What it is:** The business-rule checks that decide whether the evidence is good enough to return.
This is different from Pydantic validation — Pydantic checks *shape* ("is this field a string?"),
this file checks *meaning* ("is this data trustworthy and safe to hand out?").

**The three rule types:**
- **Coverage** — Is there enough data? For example, if only a small fraction of a population has
  skill data, the result may not be representative.
- **Freshness** — Is the data recent enough? For example, skill profiles last updated a long time ago
  may be flagged or rejected.
- **Privacy** — Is it safe to return? For example, if a population is so small that results could
  identify specific individuals, the data should be suppressed or aggregated.

**Where the thresholds come from:** Not hard-coded here — they're read from `config.py`, so they can
change per environment without touching logic.

**How it connects:** Runs after `normalization.py`, before `main.py` returns the response. Failures
raise exceptions from `errors.py` or add warnings to the response.

---

### `authorization.py` — Service identity + scopes
**What it is:** Decides whether the caller is allowed to make this request.

**What goes in it:**
- **Service identity** — figuring out *which service* is calling (in a multi-agent system, callers
  are usually other services/agents, not humans), typically from a token in the request header
- **Scopes** — checking that the caller's token grants permission for this specific action (for
  example, a scope that allows reading skill evidence)
- A FastAPI dependency (a function used with `Depends(...)`) so routes can require authorization in
  one line

**How it connects:** `main.py` attaches it to routes. Unauthorized requests are rejected before any
TechWolf call happens. Failures use the 401/403 exceptions from `errors.py`.

---

### `audit.py` — Audit / correlation logging
**What it is:** Structured logging that records who asked for what, and ties together every log line
that belongs to the same request.

**What goes in it:**
- **Correlation ID** — a unique ID for each request (read from an incoming header if the caller
  sent one, otherwise generated). Every log line and every downstream call carries it, so you can
  trace one request across multiple agents/services.
- **Audit entries** — a record of each access: which service called, which population was requested,
  when, and whether it succeeded. This matters because skills data is about employees.
- Usually implemented as FastAPI middleware so it runs on every request automatically.

**What it should *not* log:** The actual personal data being returned.

**How it connects:** Wraps every request handled by `main.py`. `techwolf_client.py` can forward the
correlation ID to TechWolf.

---

### `config.py` — Thresholds and environment config
**What it is:** The one place all settings live.

**What goes in it:**
- Environment values: TechWolf base URL, credentials, timeouts, log level
- Validation thresholds used by `validation.py` (coverage minimum, freshness window, minimum
  population size for privacy)
- Values read from environment variables / `.env` (which is already in `.gitignore`), with sensible
  defaults for local development

**Why it's its own file:** So dev, test, and production can behave differently without code changes,
and so secrets never get committed.

**How it connects:** Imported by `techwolf_client.py`, `validation.py`, `authorization.py`, and
`audit.py`.

---

### `errors.py` — Standard exception mapping
**What it is:** The service's own exception types and the rules for turning them into HTTP responses.

**What goes in it:**
- Custom exceptions, for example: TechWolf unavailable, insufficient coverage, stale data, privacy
  threshold not met, unauthorized, forbidden
- FastAPI exception handlers that map each one to a status code (e.g. 401, 403, 422, 502/503) and a
  consistent JSON error body — ideally including the correlation ID from `audit.py`

**Why it matters:** Callers (other agents) get the same predictable error format no matter what went
wrong, so they can react programmatically instead of parsing random error messages.

**How it connects:** Raised from every other module; the handlers are registered in `main.py`.

---

## `tests/` — proof it works

Each test file lines up with one part of `app/`, so a failing test points straight at the file to
fix. Tests run with `pytest` and use FastAPI's `TestClient` to call the API without starting a real
server. TechWolf is faked (mocked) in tests — you never hit the real API from the test suite.

| File | What it proves |
|------|----------------|
| `test_contract.py` | The API matches its published contract: requests/responses have the right shape, the generated OpenAPI spec is valid (`openapi-spec-validator`), and output objects match their JSON Schemas (`jsonschema`). |
| `test_validation.py` | Each coverage, freshness, and privacy rule passes good data and rejects/flags bad data — including edge cases right at the thresholds. |
| `test_authorization.py` | Missing token → rejected. Wrong scope → rejected. Correct identity + scope → allowed. |
| `test_normalization.py` | Sample TechWolf responses turn into the correct internal evidence records, including when optional fields are missing. |
| `test_failure_modes.py` | What happens when things go wrong: TechWolf timeout, TechWolf error, malformed TechWolf data. Checks that the service returns the right error from `errors.py` instead of crashing. |

---

## Root files — packaging and running

### `Dockerfile`
**What it is:** Instructions for building a container image of the service.

**What it does:** Starts from a Python base image, installs dependencies, copies in `app/`, and runs
`uvicorn app.main:app` on a port. This is how the service gets deployed so it runs the same way
everywhere, not just on your machine.

### `pyproject.toml`
**What it is:** The project's configuration file for Python tooling.

**What it does:** Declares the project name/version and dependencies, and holds settings for tools
like `pytest`. It can eventually replace `requirements.txt` as the list of dependencies (see
`dependencies.md` for what each one does).

### `README.md`
**What it is:** The front page for anyone opening the repo.

**What it covers:** What the service does, how to install and run it locally, how to run the tests,
which environment variables are needed, and a pointer to docs like this one.

---

## How a request flows through the files

```
Request: POST /v1/skills/evidence
   │
   ▼
audit.py            assign correlation ID, start audit entry
   │
   ▼
main.py             route receives the request
   │
   ├─► models.py         Pydantic checks shape (SkillEvidenceRequest)
   ├─► authorization.py  is this service allowed? (identity + scopes)
   ├─► techwolf_client.py fetch raw skills data from TechWolf
   ├─► normalization.py  convert TechWolf format → internal evidence record
   └─► validation.py     coverage / freshness / privacy checks
   │
   ▼
main.py             return response (shaped by models.py)
   │
   ▼
audit.py            log outcome with the same correlation ID

At any step, a problem raises an exception from errors.py,
which turns it into a consistent HTTP error response.
config.py supplies settings and thresholds to every step.
```

**The short version:** `main.py` orchestrates. `models.py` defines the shapes. `techwolf_client.py`
fetches, `normalization.py` translates, `validation.py` judges. `authorization.py` guards the door,
`audit.py` keeps the record, `config.py` holds the settings, and `errors.py` makes failures
predictable. Each has a matching test file.
