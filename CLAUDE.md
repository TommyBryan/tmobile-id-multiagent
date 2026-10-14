# CLAUDE.md — T-Mobile L&D Multi-Agent Ecosystem

This file gives Claude Code persistent context for this repo. Read this first in every session
before writing or changing code.

---

## Current repo layout (as of this writing)

```
tmobile-id-multiagent/
├── app/
│   └── main.py                      # Skills Data Service scaffold, verbatim from v6 §8
├── schemas/
│   └── canonical/                   # JSON Schemas for the 7 canonical objects (verbatim from v6)
├── tests/
│   └── test_canonical_schemas.py    # Checks the 7 schemas are valid Draft 2020-12 (stdlib unittest)
├── docs/
│   └── source/                      # The two source PDFs (v6 + v3), plus doc.txt placeholder
├── requirements.txt                 # fastapi, uvicorn[standard], pydantic, jsonschema,
│                                     # openapi-spec-validator — installed and confirmed working
├── dependencies.md                  # Explains each dependency and how they interact at runtime
├── project-structure.md             # Quick repo map with inline comments
├── project-structure-detailed.md    # Same structure, fuller explanations + build order + tool list
└── CLAUDE.md                        # this file
```

This repo *is* the Skills Data Service build (step 2 of the overall build order — see
`project-structure-detailed.md` for the full 11-step sequence across the whole agent mesh). It is
not yet the full multi-agent mesh; `agents/`, `orchestrator/`, and the other services come later.

---

## Source of truth

Two PDFs in `docs/source/` define this project's requirements. Read the relevant section of the
PDF itself before implementing anything from it — do not paraphrase from memory of this file for
exact schemas or code scaffolds.

1. **`T-Mobile_ID_Multi_Agent_Architecture_v6_Skills_Data_Service_API.pdf`**
   The primary architecture doc. Contains:
   - Full case-lifecycle agent mesh (Intake → Discovery → Brief-Writer → Stakeholder Review →
     Learning Architecture → Content Builder → QA/Accessibility → Scheduler/Batch →
     Notification/Nudge → Analytics & Impact → Content Iteration), governed by an Orchestrator Agent.
   - The 7 canonical data objects (Intake Object, Diagnosis Object, Skill Gap Evidence Record,
     Learner Context Object, Learning Solution Brief, QA Review Object, Impact Evidence Object).
   - **Section 8, "FastAPI Reference Implementation"** — the actual scaffold to start `app/main.py`
     from: `app = FastAPI(...)`, the `Population` / `DiagnosticContext` / `Options` /
     `SkillEvidenceRequest` Pydantic models, and the `POST /v1/skills/evidence` route.
   - **Section 9, "Suggested Codebase Structure"** — a more elaborate file tree than this repo
     currently uses; treat it as a reference, not a requirement to match exactly.
   - Security/privacy/auth requirements (Entra ID app-only tokens, least-privilege TechWolf scopes,
     aggregate-only evidence, audit logging).

2. **`T-Mobile_ID_Multi_Agent_Architecture_v3_JSON_Developer.pdf`**
   The developer/JSON-contract companion doc — Fill-In JSON references, Production Output Templates,
   and full JSON Schemas (Draft 2020-12) for every agent's input/output.

**Which doc wins for schemas:** v6. It contains every v3 agent schema unchanged, and replaces v3's
"Skills Agent" contract with the Skills Data Service's Skill Gap Evidence Record (v6 §6.3) — v6
notes two defects in the old v3 contract. Copy schemas from the PDF text, never retype them; see
`schemas/canonical/README.md` for the object → file → page mapping.

---

## Current status

- [x] Python environment created, dependencies installed and confirmed (`pip list` verified):
      `fastapi`, `uvicorn[standard]`, `pydantic`, `jsonschema`, `openapi-spec-validator`
- [x] Both source PDFs committed to `docs/source/`
- [x] `app/main.py` written as a verbatim copy of the v6 §8 scaffold; boots, serves `/docs` (200),
      and `POST /v1/skills/evidence` returns 501 "TechWolf tenant adapter not configured".
      Note: per §8, `authorize_request()` returns `True` (pass-through stub — NOT real auth);
      only `techwolf_query()` and `normalize_and_validate()` raise `NotImplementedError`
- [x] `schemas/canonical/`: the 7 canonical object schemas, extracted from the v6 PDF and
      cross-checked against the v6 .docx (identical). Tested by `tests/test_canonical_schemas.py`
- [ ] Agent-specific (non-canonical) output schemas → `schemas/agents/`; Skill Evidence Request
      (v6 §5.4) → `schemas/services/`
- [ ] No agents, no orchestrator, no Docker yet

---

## Confirmed dependencies (don't add more without checking the docs first)

```
fastapi
uvicorn[standard]
pydantic
jsonschema
openapi-spec-validator
```

Everything else (Entra ID auth library, HTTP client, test framework, linters) is intentionally
deferred — ask before adding new dependencies. The docs don't specify exact libraries for those yet,
and this project is being built incrementally, one confirmed layer at a time.

---

## Known issues / open decisions

- The `.venv` was renamed from `venv` after creation, so its scripts' shebangs point to the old
  path and bare `uvicorn` fails. Run via the interpreter instead, or recreate the venv:
  `.venv/bin/python -m uvicorn app.main:app --reload`
- Writing tests needs a new dependency: FastAPI's `TestClient` requires `httpx2`, and no test
  framework is chosen yet. Ask before adding either.
- The Diagnosis Object schema's `title` in the source doc is
  `"## 5. Learner/Org Context (from Learner Data Agent) JSON Schema"` (a template leak). Kept
  verbatim; annotation only, doesn't affect validation. Fix only if the user decides to.
- `authorize_request()` must be replaced with real Entra ID app-only token / scope / case
  authorization before the service handles anything real.

---

## Next steps (agreed plan)

Build agents as files, enforce rules in code, one working chain first:

```
agents/<agent>/prompt.md      # the agent's instructions, copied from the v6 doc
agents/<agent>/contract.json  # inputs/outputs ($ref to schemas/), allowed tools,
                              # gates it must stop at, must-never rules
orchestrator/                 # code: validates every output against schemas/, enforces HITL gates
```

1. ~~`schemas/canonical/` — the 7 objects~~ (done)
2. `agents/intake/` and `agents/discovery/` — `prompt.md` + `contract.json`
3. `agents/learner_data/` + the Skills Data Service tool contract for Discovery (v6 §13)
4. Minimal orchestrator: Intake → Discovery, schema validation, stop at Diagnosis acceptance gate
5. Remaining agents in lifecycle order

Open decision: the docs don't name the LLM runtime/agent framework — needed before agents run.
Run tests with: `.venv/bin/python -m unittest discover tests -v`

---

## Non-negotiable rules from the architecture (enforce these in code, not just docs)

- Never fabricate missing facts, data, approvals, or system states — return `insufficient_evidence`
  instead.
- Structured objects (the 7 canonical objects) are the system of record between agents — not
  conversation memory or free text.
- Human-in-the-loop gates are required before: Diagnosis acceptance, Blueprint Approval,
  Release/Go-Live Approval, Scored-bank entry, Content Iteration publish. No agent may satisfy its
  own approval gate.
- Least-privilege access to Workday, OnPoint, TechWolf, Magenta U — every service call is scoped to
  the specific case and purpose, never blanket access.
- Skills Data Service returns population-level/aggregate evidence only by default — never
  individual-level data unless separately authorized.
- Production-write services (Scheduler/Batch, Notification/Delivery) must never report fabricated
  success — see `ProductionWriteUnavailableError` and `allow_simulated` labeling requirements in the
  v6 doc. (Not relevant to this repo yet — those are built in step 9 of the overall sequence.)
