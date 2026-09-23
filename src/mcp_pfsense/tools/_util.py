"""Shared helpers for tool response shaping."""

from __future__ import annotations

import json
from typing import Any


def dumps(data: Any) -> str:
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


def pick(obj: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {k: obj[k] for k in keys if k in obj}


def slim_list(items: Any, keys: list[str] | None = None) -> Any:
    if not isinstance(items, list):
        return items
    if keys is None:
        return items
    return [pick(i, keys) if isinstance(i, dict) else i for i in items]
