"""Validate before changing persistent state."""

import json
import math

from .errors import ValidationError


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(name + " must be a nonempty string")
    return value


def positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValidationError(name + " must be a positive integer")
    return value


def positive_seconds(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(name + " must be a finite positive number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValidationError(name + " must be finite") from exc
    if not math.isfinite(result) or result <= 0:
        raise ValidationError(name + " must be a finite positive number")
    return result


def json_text(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValidationError("value must be finite JSON: " + str(exc)) from exc


def page(limit, offset):
    positive_integer(limit, "limit")
    if limit > 1000:
        raise ValidationError("limit must not exceed 1000")
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValidationError("offset must be a nonnegative integer")


def kind_filter(kinds):
    if kinds is None:
        return None
    if isinstance(kinds, (str, bytes)):
        raise ValidationError("kinds must be an iterable of kind strings")
    try:
        result = tuple(kinds)
    except TypeError as exc:
        raise ValidationError("kinds must be iterable") from exc
    for kind in result:
        text(kind, "kind")
    return result
