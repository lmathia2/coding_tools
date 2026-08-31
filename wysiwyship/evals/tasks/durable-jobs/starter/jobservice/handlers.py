"""Handler registry and useful, deterministic built-ins.

Handlers receive an isolated decoded payload and an ExecutionContext. They may
raise ordinary exceptions to request a retry. Process-control exceptions escape.
"""

import math
from string import Formatter

from .errors import HandlerNotFound, ValidationError
from .validation import text


class HandlerRegistry:
    def __init__(self):
        self._handlers = {}

    def register(self, kind, handler):
        text(kind, "kind")
        if not callable(handler):
            raise ValidationError("handler must be callable")
        if kind in self._handlers:
            raise ValidationError("handler already registered: " + kind)
        self._handlers[kind] = handler
        return self

    def resolve(self, kind):
        try:
            return self._handlers[kind]
        except KeyError as exc:
            raise HandlerNotFound("no handler for " + kind) from exc

    def kinds(self):
        return tuple(sorted(self._handlers))


def echo(payload, context):
    context.log("echo")
    return payload


def summarize(payload, context):
    if not isinstance(payload, dict) or not isinstance(payload.get("values"), list):
        raise ValidationError("summary expects an object containing a values array")
    numbers = payload["values"]
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) for value in numbers):
        raise ValidationError("summary values must be finite numbers")
    total = sum(numbers)
    context.log("summarized", count=len(numbers))
    return {"count": len(numbers), "sum": total,
            "mean": total / len(numbers) if numbers else None,
            "min": min(numbers) if numbers else None,
            "max": max(numbers) if numbers else None}


def render(payload, context):
    if not isinstance(payload, dict):
        raise ValidationError("render expects an object")
    template = text(payload.get("template"), "template")
    values = payload.get("values", {})
    if not isinstance(values, dict):
        raise ValidationError("render values must be an object")
    # Limit templates to flat fields: no attribute or index traversal.
    for _, field, spec, conversion in Formatter().parse(template):
        if field is not None and (not field.isidentifier() or spec or conversion):
            raise ValidationError("render supports only simple named fields")
    output = template.format_map(values)
    context.log("rendered", characters=len(output))
    return {"text": output}


def fail_always(payload, context):
    message = payload.get("message", "requested failure") if isinstance(payload, dict) else str(payload)
    raise RuntimeError(message)


def default_registry():
    return (HandlerRegistry().register("echo", echo).register("summary", summarize)
            .register("render", render).register("fail", fail_always))
