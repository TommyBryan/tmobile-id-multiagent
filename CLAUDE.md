# CLAUDE.md — T-Mobile L&D Multi-Agent Ecosystem

This file gives Claude Code persistent context for this repo. Read this first in every session
before writing or changing code.

---

## Current repo layout (as of this writing)

```
tmobile-id-multiagent/
├── app/
│   └── main.py                      # EMPTY — not yet written
├── tests/                           # EMPTY — no tests yet
├── docs/
│   └── source/                      # PUT THE TWO SOURCE PDFs HERE (not yet added — see below)
├── requirements.txt                 # fastapi, uvicorn[standard], pydantic, jsonschema,
│                                     # openapi-spec-validator — installed and confirmed working
├── dependencies.md                  # Explains each dependency and how they interact at runtime
├── project-structure.md             # Quick repo map with inline comments
├── project-structure-detailed.md    # Same structure, fuller explanations + build order + tool list
└── CLAUDE.md                        # this file
```

This repo *is* the Skills Data Service build (step 2 of the overall build order — see
`project-structure-detailed.md` for the full 11-step sequence across the whole agent mesh). It is
not yet the full multi-agent mesh; `agents/`, `schemas/`, and the other services come later.

---

## Source of truth — action needed

Two PDFs define this project's requirements and are **not yet in the repo**. Add them to
`docs/source/` before relying on Claude Code to reference exact schemas or code scaffolds — do not
let it paraphrase from memory of this file for anything about to be implemented.

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
   and full JSON Schemas (Draft 2020-12) for every agent's input/output. Authoritative source for any
   schema file you write.

---

## Current status

- [x] Python environment created, dependencies installed and confirmed (`pip list` verified):
      `fastapi`, `uvicorn[standard]`, `pydantic`, `jsonschema`, `openapi-spec-validator`
- [ ] Two source PDFs not yet copied into `docs/source/`
- [ ] `app/main.py` is empty — next concrete step is the FastAPI scaffold from v6 §8
- [ ] `tests/` is empty
- [ ] No schemas, no other agents, no Docker yet

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

## Immediate next step

Write `app/main.py` using the FastAPI scaffold in the v6 doc, §8 — the Pydantic models
(`Population`, `DiagnosticContext`, `Options`, `SkillEvidenceRequest`), the `POST /v1/skills/evidence`
route, and the stub functions (`authorize_request()`, `techwolf_query()`, `normalize_and_validate()`)
left as `NotImplementedError` since there are no real TechWolf credentials yet. Then run
`uvicorn app.main:app --reload` and confirm it boots and serves `/docs`.

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
