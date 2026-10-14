# Canonical Shared Objects — JSON Schemas

The 7 canonical objects are the system of record between agents. Every agent's input and output is
one of these objects. Agents must never redefine them locally; they reference these files.

All schemas are JSON Schema Draft 2020-12, copied verbatim from
`docs/source/T-Mobile_ID_Multi_Agent_Architecture_v6_Skills_Data_Service_API.pdf`. Do not edit a
schema here without a matching change in the source document (or a recorded decision below).

| File | Canonical object | Produced by | v6 PDF page |
|---|---|---|---|
| `intake_object.schema.json` | Intake Object | Intake Agent | 7 |
| `diagnosis_object.schema.json` | Diagnosis Object | Discovery Agent | 14 |
| `skill_gap_evidence_record.schema.json` | Skill Gap Evidence Record | Skills Data Service (`app/`) | 22 (§6.3) |
| `learner_context_object.schema.json` | Learner Context Object | Learner Data Agent | 32 |
| `learning_solution_brief.schema.json` | Learning Solution Brief | Brief-Writer Agent | 38 |
| `qa_review_object.schema.json` | QA Review Object | QA/Accessibility Reviewer Agent | 80 |
| `impact_evidence_object.schema.json` | Impact Evidence Object | Analytics & Impact Agent | 89 |

## Source notes

- **v6 over v3.** For six of the seven objects, the v6 and v3 schemas are identical. The Skill Gap
  Evidence Record differs: v6 replaced v3's "Skills Agent" contract with the Skills Data Service
  contract (§6.3). v6 also records two defects in the old v3 contract (a placeholder `"[skill]"`
  property name in `proficiency_distribution`, and a combined date/status string in
  `data_freshness`). Using v6 avoids both.
- **Known issue — Diagnosis Object title.** In the source document, the Diagnosis Object schema's
  `title` is `"## 5. Learner/Org Context (from Learner Data Agent) JSON Schema"`, which looks like a
  heading that leaked in from a template. It is kept verbatim here. `title` is an annotation only
  and does not affect validation.
- Most schemas are titled `"Agent Output Contract"` in the source; the file name, not the title,
  identifies the object.
