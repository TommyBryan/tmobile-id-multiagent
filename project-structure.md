# Suggested Codebase Structure

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
