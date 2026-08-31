#!/usr/bin/env python3
"""Load and validate WYSIWYShip model profiles."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PLATFORMS = {"codex", "copilot", "claude_code", "pi"}
WORKFLOWS = {"dev", "review_pr"}
ROLES = {"normal", "deep", "fast", "top"}


def validate_model(path: str, model: object, allow_inherit: bool) -> None:
    if model is None:
        if allow_inherit:
            return
        raise RuntimeError(f"{path}.model must be a non-empty string")
    if not isinstance(model, str) or not model.strip():
        raise RuntimeError(f"{path}.model must be null or a non-empty string")


def validate_spec(path: str, spec: object, allow_inherit: bool) -> None:
    if not isinstance(spec, dict):
        raise RuntimeError(f"{path} must be an object")
    if not {"model", "reasoning"}.issubset(spec):
        raise RuntimeError(f"{path} requires model and reasoning")
    if set(spec) - {"model", "reasoning", "notes"}:
        raise RuntimeError(f"{path} must contain only model, reasoning, and optional notes")
    validate_model(path, spec.get("model"), allow_inherit)
    reasoning = spec.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        raise RuntimeError(f"{path}.reasoning must be a non-empty string")
    if "notes" in spec and not isinstance(spec["notes"], str):
        raise RuntimeError(f"{path}.notes must be a string")


def validate_platform(path: str, platform: str, settings: object) -> None:
    if not isinstance(settings, dict) or set(settings) != {"workflows", "roles"}:
        raise RuntimeError(f"{path} must define exactly workflows and roles")
    workflows = settings["workflows"]
    roles = settings["roles"]
    if not isinstance(workflows, dict) or set(workflows) != WORKFLOWS:
        raise RuntimeError(f"{path}.workflows must define {sorted(WORKFLOWS)}")
    if not isinstance(roles, dict) or set(roles) != ROLES:
        raise RuntimeError(f"{path}.roles must define {sorted(ROLES)}")
    allow_inherit = True
    for name, spec in workflows.items():
        validate_spec(f"{path}.workflows.{name}", spec, allow_inherit)
    for name, spec in roles.items():
        validate_spec(f"{path}.roles.{name}", spec, allow_inherit)


def validate_profiles(profiles: dict[str, Any]) -> None:
    for profile_name, profile in profiles.items():
        path = f"profiles.{profile_name}"
        if not profile_name.strip():
            raise RuntimeError("profile names must be non-empty")
        if not isinstance(profile, dict) or set(profile) != PLATFORMS:
            raise RuntimeError(f"{path} must define {sorted(PLATFORMS)}")
        for platform in PLATFORMS:
            validate_platform(f"{path}.{platform}", platform, profile[platform])


def validate_config(config: object) -> dict[str, Any]:
    if not isinstance(config, dict) or set(config) != {"schema_version", "active_profile", "profiles"}:
        raise RuntimeError("models.json must define exactly schema_version, active_profile, and profiles")
    if config.get("schema_version") != 2:
        raise RuntimeError("models.json schema_version must be 2")
    profiles = config.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise RuntimeError("models.json profiles must be a non-empty object")
    active = config.get("active_profile")
    if not isinstance(active, str) or active not in profiles:
        raise RuntimeError("models.json active_profile must name an existing profile")
    validate_profiles(profiles)
    return config


def load_config(path: Path) -> dict[str, Any]:
    return validate_config(json.loads(path.read_text(encoding="utf-8")))


def get_profile(config: dict[str, Any], name: str | None = None) -> tuple[str, dict[str, Any]]:
    selected = name or config["active_profile"]
    if selected not in config["profiles"]:
        choices = ", ".join(sorted(config["profiles"]))
        raise RuntimeError(f"unknown model profile {selected!r}; choose one of: {choices}")
    return selected, config["profiles"][selected]


def resolve_spec(
    profile: dict[str, Any],
    platform: str,
    role: str,
    workflow: str | None = None,
) -> dict[str, Any]:
    settings = profile[platform]
    if role == "coordinator":
        if workflow not in WORKFLOWS:
            raise RuntimeError(f"coordinator requires workflow in {sorted(WORKFLOWS)}")
        return settings["workflows"][workflow]
    if workflow is not None:
        raise RuntimeError(f"specialist role {role!r} must not declare a workflow")
    if role not in ROLES:
        raise RuntimeError(f"unknown model role {role!r}")
    return settings["roles"][role]
