#!/usr/bin/env python3
"""Render a validated Project ELI5 story as one dependency-free HTML file."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / "assets/project-eli5-template.html"
DEFAULT_AUDIENCE = "Curious developer"
ACCENTS = {"coral", "mint", "gold", "sky", "violet"}
SLIDE_TEXT_LIMITS = {"eyebrow": 40, "title": 90, "body": 700, "code": 1200}
RECORD_SCHEMAS = {
    "items": ({"title": 80, "body": 260, "tag": 24}, 4),
    "metrics": ({"value": 32, "label": 80, "detail": 180}, 4),
}


def load_story(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("story root must be a JSON object")
    return data


def validate_text(value: object, label: str, maximum: int, required: bool = False) -> None:
    if value is None and not required:
        return
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError(f"{label} must be a non-empty string")
    if len(value) > maximum:
        raise ValueError(f"{label} exceeds {maximum} characters")


def validate_text_fields(data: dict[str, Any], schema: dict[str, int], label: str, required: set[str] | None = None) -> None:
    required = required or set()
    for key, maximum in schema.items():
        validate_text(data.get(key), f"{label}.{key}", maximum, key in required)


def validate_string_list(value: object, label: str, maximum_items: int, maximum_length: int) -> None:
    if value is None:
        return
    if not isinstance(value, list) or len(value) > maximum_items:
        raise ValueError(f"{label} must be an array with at most {maximum_items} entries")
    for index, item in enumerate(value):
        validate_text(item, f"{label}[{index}]", maximum_length, True)


def validate_records(value: object, label: str, schema: dict[str, int], maximum_items: int) -> None:
    if value is None:
        return
    if not isinstance(value, list) or len(value) > maximum_items:
        raise ValueError(f"{label} must be an array with at most {maximum_items} entries")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        validate_text_fields(item, schema, f"{label}[{index}]", {next(iter(schema))})


def validate_analogy(value: object, label: str) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    validate_text_fields(value, {"title": 100, "body": 500, "boundary": 300}, label, {"title", "body"})


def validate_slide(slide: object, index: int) -> None:
    label = f"slides[{index}]"
    if not isinstance(slide, dict):
        raise ValueError(f"{label} must be an object")
    validate_text_fields(slide, SLIDE_TEXT_LIMITS, label, {"title"})
    validate_string_list(slide.get("bullets"), f"{label}.bullets", 5, 180)
    for key, (schema, maximum) in RECORD_SCHEMAS.items():
        validate_records(slide.get(key), f"{label}.{key}", schema, maximum)
    validate_analogy(slide.get("analogy"), f"{label}.analogy")
    populated = [key for key in ("bullets", "items", "metrics", "analogy", "code") if slide.get(key)]
    if len(populated) > 1:
        raise ValueError(f"{label} may use only one structured element, found {populated}")
    accent = slide.get("accent")
    if accent is not None and accent not in ACCENTS:
        raise ValueError(f"{label}.accent must be one of {sorted(ACCENTS)}")


def validate_story(story: dict[str, Any]) -> None:
    validate_text_fields(
        story,
        {"title": 100, "subtitle": 180, "audience": 100, "summary": 400},
        "story",
        {"title", "summary"},
    )
    slides = story.get("slides")
    if not isinstance(slides, list) or not 3 <= len(slides) <= 9:
        raise ValueError("story.slides must contain 3 to 9 slides")
    for index, slide in enumerate(slides):
        validate_slide(slide, index)
    closing = story.get("closing")
    if closing is not None:
        if not isinstance(closing, dict):
            raise ValueError("story.closing must be an object")
        validate_text_fields(closing, {"title": 100, "body": 500}, "story.closing")
        validate_string_list(closing.get("next_steps"), "story.closing.next_steps", 4, 180)


def safe_json(story: dict[str, Any]) -> str:
    encoded = json.dumps(story, ensure_ascii=False, separators=(",", ":"))
    return encoded.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")


def render_document(story: dict[str, Any], template_path: Path = TEMPLATE) -> str:
    normalized = dict(story)
    if not normalized.get("audience"):
        normalized["audience"] = DEFAULT_AUDIENCE
    validate_story(normalized)
    template = template_path.read_text(encoding="utf-8")
    if template.count("__STORY_DATA__") != 1:
        raise ValueError("ELI5 template must contain exactly one __STORY_DATA__ marker")
    document = template.replace("__STORY_DATA__", safe_json(normalized))
    forbidden = ("http://", "https://", "<script src=", "<link rel=\"stylesheet\"")
    present = [value for value in forbidden if value in document.lower()]
    if present:
        raise ValueError(f"rendered explainer contains external dependency markers: {present}")
    return document


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(raw)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="story JSON path")
    parser.add_argument("--output", type=Path, help="destination HTML path")
    parser.add_argument("--check", action="store_true", help="validate and render in memory without writing")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    args = parser.parse_args()

    story = load_story(args.input)
    document = render_document(story)
    if args.check:
        print(f"ELI5 story valid: {len(story['slides']) + 2} rendered slides")
        return 0
    if args.output is None:
        parser.error("--output is required unless --check is used")
    if args.output.exists() and not args.force:
        parser.error(f"output already exists: {args.output}; use --force to replace it")
    write_atomic(args.output, document)
    print(f"wrote {len(story['slides']) + 2} slides to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
