import json
import tempfile
import unittest
from pathlib import Path

from src.reconciliation import reconcile
from src.transformer import parse_xml, write_json


SAMPLE = """<clients>
<client><id>A1</id><name>Asha</name><email>asha@example.com</email><phone>123</phone><created_at>2026-01-01</created_at></client>
<client><id>A2</id><name>Broken</name><email>bad-email</email><phone>456</phone><created_at>not-a-date</created_at></client>
</clients>"""


class TransformerTests(unittest.TestCase):
    def test_parses_valid_record_and_reports_invalid_record(self):
        with tempfile.TemporaryDirectory() as folder:
            xml_path = Path(folder) / "input.xml"
            xml_path.write_text(SAMPLE, encoding="utf-8")
            records, errors = parse_xml(xml_path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["client_id"], "A1")
        self.assertEqual(len(errors), 2)

    def test_invalid_xml_returns_error(self):
        with tempfile.TemporaryDirectory() as folder:
            xml_path = Path(folder) / "bad.xml"
            xml_path.write_text("<clients>", encoding="utf-8")
            records, errors = parse_xml(xml_path)

        self.assertEqual(records, [])
        self.assertEqual(errors[0]["field"], "xml")

    def test_reconciliation_finds_mismatch_and_missing_row(self):
        imported = [
            {"client_id": "A1", "name": "Asha", "email": "new@example.com", "phone": "123", "created_at": "2026-01-01"},
            {"client_id": "A2", "name": "Bob", "email": "bob@example.com", "phone": "456", "created_at": "2026-01-01"},
        ]
        reference = {
            "A1": {"name": "Asha", "email": "asha@example.com", "phone": "123", "created_at": "2026-01-01"}
        }
        report = reconcile(imported, reference)
        self.assertEqual(report["matched_records"], 0)
        self.assertEqual(report["discrepancy_count"], 2)

    def test_json_output_is_valid_json(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "nested" / "out.json"
            write_json([{"client_id": "A1"}], output)
            self.assertEqual(json.loads(output.read_text()), [{"client_id": "A1"}])


if __name__ == "__main__":
    unittest.main()
