```
my-multi-agent-system/
├── .env                            # Environment variables (ANTHROPIC_API_KEY, etc.)
├── .gitignore
├── requirements.txt
│
├── config/                         # PROMPT & CONTRACT DEFINITIONS
│   ├── agents/                     # 13 System Prompts in Markdown format
│   │   ├── 01_intake.md
│   │   ├── 02_discovery.md
│   │   ├── 03_skills.md
│   │   ├── 04_learner_data.md
│   │   ├── 05_brief_writer.md
│   │   ├── 06_qa_reviewer.md
│   │   ├── 07_stakeholder.md
│   │   ├── 08_content_iteration.md
│   │   ├── 09_analytics.md
│   │   ├── 10_notification.md
│   │   ├── 11_scheduler.md
│   │   ├── 12_orchestrator.md
│   │   └── 13_human_review.md
│   │
│   └── schemas/                    # Machine-Enforceable Output Contracts
│       ├── intake_contract.json
│       ├── discovery_contract.json
│       ├── skills_contract.json
│       ├── brief_contract.json
│       └── ... (matching contract schema per agent)
│
├── src/                            # PYTHON EXECUTABLE SOURCE CODE
│   ├── __init__.py
│   ├── config_loader.py            # Utility to load .md prompts and parse .json schemas
│   │
│   ├── models/                     # Type-safe execution contracts (Pydantic)
│   │   ├── __init__.py
│   │   ├── intake_model.py         # Matches config/schemas/intake_contract.json
│   │   ├── discovery_model.py
│   │   └── ...
│   │
│   ├── agents/                     # Agent Definitions
│   │   ├── __init__.py
│   │   ├── intake_agent.py
│   │   ├── discovery_agent.py
│   │   └── ...
│   │
│   ├── tasks/                      # Task Orchestrations
│   │   ├── __init__.py
│   │   ├── intake_tasks.py
│   │   ├── diagnosis_tasks.py
│   │   └── ...
│   │
│   └── flows/                      # Execution Stages & Pipelines
│       ├── __init__.py
│       ├── stage_1_intake_flow.py  # Phase 1: Pre-screening & routing
│       ├── stage_2_diagnose_flow.py# Phase 2: Root cause & skill gaps
│       └── stage_3_design_flow.py  # Phase 3: Solution design & sign-off
│
├── main.py                         # Master entry point (orchestrates execution flows)
└── tests/                          # Unit and integration tests
    ├── test_intake_contract.py
    └── test_flows.py
```
