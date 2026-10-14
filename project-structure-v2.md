# Suggested Codebase Structure

## Full repo layout (multi-agent mesh)

Legend: ✅ exists · 🆕 added in the latest step · ⬜ planned

```
tmobile-id-multiagent/
├── app/                                  ✅ Skills Data Service (FastAPI, v6 §8)
│   └── main.py                           ✅   later split per v6 §9: models, techwolf_client,
│                                               normalization, validation, authorization, audit…
│
├── schemas/                              ← the shared data rules every agent follows
│   ├── canonical/                        🆕 the 7 shared objects (system of record)
│   │   ├── intake_object.schema.json
│   │   ├── diagnosis_object.schema.json
│   │   ├── skill_gap_evidence_record.schema.json
│   │   ├── learner_context_object.schema.json
│   │   ├── learning_solution_brief.schema.json
│   │   ├── qa_review_object.schema.json
│   │   ├── impact_evidence_object.schema.json
│   │   └── README.md
│   ├── agents/                           ⬜ outputs that aren't one of the 7 objects
│   │   ├── stakeholder_review_record.schema.json
│   │   ├── learning_architecture.schema.json
│   │   ├── content_package.schema.json
│   │   ├── assessment.schema.json
│   │   ├── scheduling_batch_plan.schema.json
│   │   ├── notification.schema.json
│   │   ├── content_iteration.schema.json
│   │   └── orchestrator_transition.schema.json
│   └── services/                         ⬜ service request schemas
│       └── skill_evidence_request.schema.json    (v6 §5.4)
│
├── agents/                               ⬜ one folder per agent, same 2 files each
│   ├── intake/
│   │   ├── prompt.md                     ⬜   the agent's instructions (from v6/v3)
│   │   └── contract.json                 ⬜   inputs/outputs → $ref to schemas/,
│   │                                           allowed tools, gates it must stop at,
│   │                                           must-never rules
│   ├── discovery/                        ⬜   ← build these two first
│   ├── learner_data/
│   ├── brief_writer/
│   ├── stakeholder_review/
│   ├── learning_architecture/
│   ├── content_builder/                  (+ storyline, vyond, scenario, job_aid, assessment sub-agents)
│   ├── qa_accessibility/                 (2 modes: brief review, content quality)
│   ├── scheduler_batch/
│   ├── notification_nudge/
│   ├── analytics_impact/
│   └── content_iteration/
│
├── orchestrator/                         ⬜ the case manager, written as code (not just a prompt)
│   ├── prompt.md                         ⬜   Master Orchestrator prompt (v6)
│   ├── gates.py                          ⬜   human-approval gates; no agent can approve its own
│   ├── validate.py                       ⬜   checks every agent output against schemas/
│   └── run_case.py                       ⬜   runs Intake → Discovery → … for one case
│
├── tests/
│   ├── test_canonical_schemas.py         🆕
│   ├── test_agent_contracts.py           ⬜   every contract.json's references resolve to real schemas
│   └── …                                 ⬜   Skills Data Service tests (v6 §16)
│
├── docs/source/                          ✅ v6 + v3 PDFs (source of truth)
├── requirements.txt                      ✅
└── CLAUDE.md                             ✅
```

The section below is the v6 §9 target layout for the Skills Data Service itself — what `app/`
grows into once `main.py` is split up.

---

## Skills Data Service layout (v6 §9)

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
