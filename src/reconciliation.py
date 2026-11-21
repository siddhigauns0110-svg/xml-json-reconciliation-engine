"""Compare imported client records with a reference data source."""
from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any


COMPARE_FIELDS = ("name", "email", "phone", "created_at")


def load_csv_reference(path: str | Path) -> dict[str, dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return {row["client_id"]: row for row in csv.DictReader(handle)}


def load_mysql_reference() -> dict[str, dict[str, str]]:
    """Load reference records from MySQL using MYSQL_* environment variables."""
    try:
        import mysql.connector
    except ImportError as exc:
        raise RuntimeError("Install dependencies with: pip install -r requirements.txt") from exc

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT client_id, name, email, phone, created_at FROM client_records")
        rows = cursor.fetchall()
        return {
            str(row["client_id"]): {
                key: row[key].isoformat() if hasattr(row[key], "isoformat") else str(row[key] or "")
                for key in ("client_id", *COMPARE_FIELDS)
            }
            for row in rows
        }
    finally:
        connection.close()


def reconcile(
    imported: list[dict[str, Any]],
    reference: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Classify missing reference rows and field-level mismatches."""
    discrepancies: list[dict[str, str]] = []
    matched = 0

    for record in imported:
        client_id = str(record["client_id"])
        existing = reference.get(client_id)
        if existing is None:
            discrepancies.append({
                "client_id": client_id,
                "field": "client_id",
                "imported_value": client_id,
                "reference_value": "",
                "issue": "NOT_FOUND_IN_REFERENCE",
            })
            continue

        mismatches = 0
        for field in COMPARE_FIELDS:
            imported_value = str(record.get(field) or "").strip()
            reference_value = str(existing.get(field) or "").strip()
            if imported_value != reference_value:
                mismatches += 1
                discrepancies.append({
                    "client_id": client_id,
                    "field": field,
                    "imported_value": imported_value,
                    "reference_value": reference_value,
                    "issue": "VALUE_MISMATCH",
                })
        if mismatches == 0:
            matched += 1

    return {
        "total_imported": len(imported),
        "matched_records": matched,
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
    }


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    import json

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
