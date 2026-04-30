from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from jsonschema import validators

from app.schemas.document import DocumentProcessResponse
from app.schemas.lesson import LessonCompileResponse, LessonSummary
from app.schemas.qa import CourseQAResponse


def _repo_root() -> Path:
    # apps/api/tests/unit/test_contracts.py -> parents[4] = monorepo root
    return Path(__file__).resolve().parents[4]


def _load_schema(name: str) -> dict:
    p = _repo_root() / "packages" / "schemas" / "json" / name
    return json.loads(p.read_text(encoding="utf-8"))


def _load_example(name: str) -> dict:
    p = _repo_root() / "packages" / "schemas" / "examples" / name
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_jsonschema(instance: dict, schema: dict) -> None:
    cls = validators.validator_for(schema)
    cls.check_schema(schema)
    cls(schema).validate(instance)


def test_internal_health_example_jsonschema():
    raw = _load_example("internal-health.valid.json")
    schema = _load_schema("internal-health.schema.json")
    _validate_jsonschema(raw, schema)


def test_internal_ready_example_jsonschema():
    raw = _load_example("internal-ready.valid.json")
    schema = _load_schema("internal-ready.schema.json")
    _validate_jsonschema(raw, schema)


def test_document_process_response_example():
    raw = _load_example("document-process-response.valid.json")
    schema = _load_schema("document-process-response.schema.json")
    _validate_jsonschema(raw, schema)
    DocumentProcessResponse.model_validate(raw)


def test_course_qa_response_example_matches_pydantic_and_jsonschema():
    raw = _load_example("course-qa-response.valid.json")
    schema = _load_schema("course-qa-response.schema.json")
    _validate_jsonschema(raw, schema)
    model = CourseQAResponse.model_validate(raw)
    assert model.mode in ("llm", "extractive")


def test_lesson_compile_response_example():
    raw = _load_example("lesson-compile-response.valid.json")
    schema = _load_schema("lesson-compile-response.schema.json")
    _validate_jsonschema(raw, schema)
    LessonCompileResponse.model_validate(raw)


def test_lesson_compile_response_async_example():
    raw = _load_example("lesson-compile-response.async.valid.json")
    schema = _load_schema("lesson-compile-response.schema.json")
    _validate_jsonschema(raw, schema)
    LessonCompileResponse.model_validate(raw)


def test_lesson_summary_example():
    raw = _load_example("lesson-summary.valid.json")
    schema = _load_schema("lesson-summary.schema.json")
    _validate_jsonschema(raw, schema)
    LessonSummary.model_validate(raw)
