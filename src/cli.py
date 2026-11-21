"""Command-line entry point for the XML integration workflow."""
from __future__ import annotations

import argparse
from pathlib import Path

from src.reconciliation import load_csv_reference, load_mysql_reference, reconcile, write_report
from src.transformer import parse_xml, write_errors, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Transform XML client data into JSON and reconcile records.")
    parser.add_argument("--xml", required=True, help="Input XML file")
    parser.add_argument("--json-output", default="output/clients.json")
    parser.add_argument("--errors-output", default="output/errors.json")
    parser.add_argument("--reference-csv", help="CSV reference file for local demo reconciliation")
    parser.add_argument("--mysql", action="store_true", help="Use MySQL client_records as reference data")
    parser.add_argument("--reconciliation-output", default="output/reconciliation.json")
    args = parser.parse_args()

    if args.reference_csv and args.mysql:
        parser.error("Choose either --reference-csv or --mysql, not both.")

    records, errors = parse_xml(args.xml)
    write_json(records, args.json_output)
    write_errors(errors, args.errors_output)

    print(f"Valid records: {len(records)} | Validation errors: {len(errors)}")
    print(f"JSON written to: {args.json_output}")
    print(f"Errors written to: {args.errors_output}")

    if args.reference_csv or args.mysql:
        reference = load_csv_reference(args.reference_csv) if args.reference_csv else load_mysql_reference()
        report = reconcile(records, reference)
        write_report(report, args.reconciliation_output)
        print(f"Reconciliation report written to: {args.reconciliation_output}")
        print(f"Matched: {report['matched_records']} | Discrepancies: {report['discrepancy_count']}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
