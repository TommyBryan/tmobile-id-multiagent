# Dependencies — What They Are and How They Interact

This covers only what's confirmed in the T-Mobile L&D architecture doc, plus the one thing FastAPI
literally cannot run without. Nothing here is speculative — every package below is either named in
the doc's code scaffold, or required for that scaffold to actually execute.

---

## The five packages

### 1. FastAPI
**What it is:** A Python framework for building web APIs. You write Python functions, decorate them
with a route (like `@app.post("/v1/skills/evidence")`), and FastAPI turns them into a working HTTP
endpoint.

**What it does in this project:** It's the skeleton of the Skills Data Service. The doc's scaffold
builds the app with `app = FastAPI(title="Skills Data Service", version="1.0.0")` and defines the
`POST /v1/skills/evidence` route on top of it.

**Analogy for you:** Same role Flask plays in your other projects — FastAPI is "Flask, but built
specifically for APIs," with request validation built in instead of bolted on.

---

### 2. Uvicorn
**What it is:** A server program that actually runs your FastAPI app and listens for incoming
requests on a port.

**What it does in this project:** FastAPI by itself is just Python code — nothing is listening for
traffic until something runs it. Uvicorn is that something. This is why it's on the list even though
the doc never names it directly: `app = FastAPI(...)` does nothing on its own.

**Analogy for you:** Like `flask run` — FastAPI is the app, Uvicorn is the command that boots it.

**How it connects to #1:** Uvicorn imports and runs the `app` object that FastAPI created. You'll
start the service with something like `uvicorn app.main:app --reload`.

---

### 3. Pydantic
**What it is:** A data-validation library. You define a class describing what a piece of data should
look like, and Pydantic checks every request/response against it automatically.

**What it does in this project:** Every object in the doc's scaffold — `Population`,
`DiagnosticContext`, `Options`, `SkillEvidenceRequest` — is a Pydantic model. When a request hits
your FastAPI endpoint, FastAPI hands it to Pydantic first. If the JSON doesn't match the model
(wrong type, missing required field), the request gets rejected automatically — your route code never
even runs.

**How it connects to #1:** FastAPI is built on top of Pydantic. You almost never use one without the
other — FastAPI calls into Pydantic on every single request to validate the body before your function
executes.

---

### 4. jsonschema
**What it is:** A separate, general-purpose library that checks whether a JSON object matches a
JSON Schema file (a `.json` file that describes allowed fields, types, and required values).

**What it does in this project:** The doc defines seven canonical objects (Intake Object, Diagnosis
Object, Skill Gap Evidence Record, etc.), each with its own JSON Schema. `jsonschema` is what you'd
use in a test to confirm that, say, a Diagnosis Object your code produced actually has every required
field in the right shape — independent of whether FastAPI/Pydantic already validated it on the way
in.

**How it's different from Pydantic:** Pydantic validates data *inside your running app*, tied to
Python classes. `jsonschema` validates a JSON *schema file* directly — useful for testing that your
schema files themselves are internally consistent, or for validating objects that pass between agents
outside of a single FastAPI request/response cycle.

---

### 5. openapi-spec-validator
**What it is:** A linter for OpenAPI specification files (the `.yaml` files that describe an API's
shape — its endpoints, request/response formats, auth requirements).

**What it does in this project:** The doc says all four API specs (Skill Data, Scheduler/Batch,
Notification/Delivery, Analytics & Impact) "validate clean against openapi-spec-validator." You'd run
this against each `.yaml` spec file to catch structural errors before anyone tries to build against a
broken contract.

**How it connects to the others:** It doesn't touch your running code at all — it only checks the
*documentation* of your API (the OpenAPI spec) for correctness. FastAPI can actually auto-generate
this spec for you from your Pydantic models, which is one reason the two pair so naturally.

---

## How they interact — the full picture

```
                    ┌─────────────────────────────────────┐
                    │              Uvicorn                 │
                    │   (starts the server, listens for    │
                    │        incoming HTTP requests)        │
                    └────────────────┬──────────────────────┘
                                     │ runs
                                     ▼
                    ┌─────────────────────────────────────┐
                    │              FastAPI                  │
                    │   (defines routes, e.g. POST          │
                    │    /v1/skills/evidence)                │
                    └────────────────┬──────────────────────┘
                                     │ validates every request/response against
                                     ▼
                    ┌─────────────────────────────────────┐
                    │             Pydantic                  │
                    │   (Population, DiagnosticContext,     │
                    │    Options, SkillEvidenceRequest)      │
                    └─────────────────────────────────────┘

        (separately, not part of the live request path)

┌─────────────────────────┐          ┌─────────────────────────────────┐
│       jsonschema          │          │     openapi-spec-validator        │
│  checks canonical JSON    │          │  checks your .yaml OpenAPI spec   │
│  objects against their    │          │  files are structurally valid     │
│  .schema.json files       │          │  before anyone builds against     │
│  (used in tests)          │          │  them                             │
└─────────────────────────┘          └─────────────────────────────────┘
```

**Plain-language walkthrough of a request:**

1. You start the service: `uvicorn app.main:app --reload`. Uvicorn boots up and starts listening.
2. A request comes in to `POST /v1/skills/evidence`. FastAPI catches it because that route is
   registered.
3. Before your function code runs, FastAPI hands the incoming JSON to Pydantic, which checks it
   against `SkillEvidenceRequest`. If something's missing or the wrong type, the request is rejected
   right there with a clear error — you never have to write that validation by hand.
4. Your function runs, does its work, and returns data shaped like the response model. FastAPI runs
   Pydantic again on the way out, to make sure what you're sending back also matches the expected
   shape.
5. `jsonschema` and `openapi-spec-validator` aren't part of this live request cycle at all — they're
   tools you run separately (usually in tests or CI) to double-check that your schema files and
   OpenAPI spec files are correct on their own terms.

**The short version:** Uvicorn runs FastAPI. FastAPI leans on Pydantic for every request. jsonschema
and openapi-spec-validator are quality checks that run on the side, checking your schema/spec files
rather than live traffic.
