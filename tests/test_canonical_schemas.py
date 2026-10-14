import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas" / "canonical"

CANONICAL_OBJECTS = [
    "intake_object",
    "diagnosis_object",
    "skill_gap_evidence_record",
    "learner_context_object",
    "learning_solution_brief",
    "qa_review_object",
    "impact_evidence_object",
]


def load_schema(name):
    with open(SCHEMA_DIR / f"{name}.schema.json") as f:
        return json.load(f)


class TestCanonicalSchemas(unittest.TestCase):
    def test_exactly_the_seven_canonical_objects_exist(self):
        found = sorted(p.name.removesuffix(".schema.json") for p in SCHEMA_DIR.glob("*.schema.json"))
        self.assertEqual(found, sorted(CANONICAL_OBJECTS))

    def test_each_schema_is_valid_draft_2020_12(self):
        for name in CANONICAL_OBJECTS:
            with self.subTest(schema=name):
                schema = load_schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                Draft202012Validator.check_schema(schema)

    def test_each_schema_rejects_unknown_top_level_fields(self):
        for name in CANONICAL_OBJECTS:
            with self.subTest(schema=name):
                self.assertIs(load_schema(name).get("additionalProperties"), False)

    def test_each_schema_rejects_an_empty_object(self):
        for name in CANONICAL_OBJECTS:
            with self.subTest(schema=name):
                validator = Draft202012Validator(load_schema(name))
                self.assertFalse(validator.is_valid({}))


if __name__ == "__main__":
    unittest.main()
