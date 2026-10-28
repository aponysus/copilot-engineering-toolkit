"""A synthetic item-count API and its local consumers."""

import json


def response(count: int) -> str:
    return json.dumps({"count": count})


def dashboard(payload: str) -> str:
    count = json.loads(payload)["count"]
    return f"{count + 1} including the pending item"


def export_row(payload: str) -> str:
    count = json.loads(payload)["count"]
    return f"items,{count:d}"


def destinations(payload: str, export_enabled: bool) -> list[str]:
    outputs = [dashboard(payload)]
    if export_enabled:
        outputs.append(export_row(payload))
    return outputs
