"""Parse client XML records, validate them and normalize to JSON-ready dictionaries."""
from __future__ import annotations

import re
from defusedxml import ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ("client_id", "name", "email", "created_at")


def _text(parent: ET.Element, tag: str) -> str:
    node = parent.find(tag)
    return (node.text or "").strip() if node is not None else ""


def parse_xml(xml_path: str | Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Return normalized records and validation errors from a client XML file."""
    try:
        root = ET.parse(xml_path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [], [{"record": "document", "field": "xml", "message": str(exc)}]

    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for index, node in enumerate(root.findall(".//client"), start=1):
        raw = {
            "client_id": _text(node, "id"),
            "name": _text(node, "name"),
            "email": _text(node, "email"),
            "phone": _text(node, "phone"),
            "created_at": _text(node, "created_at"),
        }
        record_errors: list[dict[str, str]] = []
        for field in REQUIRED_FIELDS:
            if not raw[field]:
                record_errors.append({"record": str(index), "field": field, "message": "Required value is missing"})

        if raw["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", raw["email"]):
            record_errors.append({"record": str(index), "field": "email", "message": "Invalid email format"})
        if raw["created_at"]:
            try:
                date.fromisoformat(raw["created_at"])
            except ValueError:
                record_errors.append({"record": str(index), "field": "created_at", "message": "Expected YYYY-MM-DD"})
        if raw["client_id"] in seen_ids and raw["client_id"]:
            record_errors.append({"record": str(index), "field": "client_id", "message": "Duplicate client ID in XML"})
        if raw["client_id"]:
            seen_ids.add(raw["client_id"])

        if record_errors:
            errors.extend(record_errors)
            continue

        records.append({
            **raw,
            "source": "xml_import",
        })

    return records, errors


def write_json(records: list[dict[str, Any]], output_path: str | Path) -> None:
    """Write records as UTF-8 JSON with stable indentation."""
    import json

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_errors(errors: list[dict[str, str]], output_path: str | Path) -> None:
    import json

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(errors, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
