# XML-to-JSON Data Transformation & Reconciliation Engine

A Python command-line project that ingests client records from XML, validates and normalizes the data, exports clean records as JSON, and compares them with a reference dataset to identify missing records and field-level mismatches.

This project demonstrates practical data-integration concepts used when different systems exchange structured data in different formats.

## What it does

1. Reads client records from an XML file.
2. Validates required fields, email formats, ISO dates, and duplicate client IDs.
3. Converts valid records into a consistent JSON structure.
4. Writes validation errors to a separate JSON file.
5. Optionally reconciles imported records against a CSV file or a MySQL reference table.
6. Produces a discrepancy report showing records that are missing or have mismatched values.

## Workflow

```text
XML input
   |
   v
XML parsing
   |
   v
Validation & normalization
   |----------------------> Validation errors (JSON)
   v
Clean JSON output
   |
   v
Reference comparison (CSV / MySQL)
   |
   v
Reconciliation report (JSON)
```

## Features

- XML parsing with `defusedxml`
- Required-field and duplicate-ID validation
- Email and date-format validation
- Normalized JSON output
- Field-by-field data comparison
- CSV reference mode for a quick local demo
- Optional MySQL reference-data integration
- Command-line interface
- Unit tests using Python's built-in `unittest`

## Tech stack

- **Language:** Python 3.10+
- **Data formats:** XML, JSON, CSV
- **Database:** MySQL (optional)
- **Libraries:** defusedxml, mysql-connector-python, python-dotenv
- **Testing:** unittest
- **Tools:** Git and GitHub

## Project structure

```text
xml-json-reconciliation-engine/
├── examples/
│   ├── reference_clients.csv
│   └── sample_clients.xml
├── sql/
│   └── schema.sql
├── src/
│   ├── __init__.py
│   ├── cli.py
│   ├── reconciliation.py
│   └── transformer.py
├── tests/
│   └── test_transformer.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/siddhigauns0110-svg/xml-json-reconciliation-engine.git
cd xml-json-reconciliation-engine
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:
```bash
.venv\\Scripts\\activate
```

macOS / Linux:
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the project

### Convert XML records into JSON

```bash
python -m src.cli --xml examples/sample_clients.xml
```

By default, generated files are written to the `output/` directory:
- `output/clients.json` — valid normalized records
- `output/errors.json` — validation errors

### Run reconciliation using the sample CSV

```bash
python -m src.cli --xml examples/sample_clients.xml --reference-csv examples/reference_clients.csv
```

This also generates `output/reconciliation.json`, containing the matched-record count and any discrepancies.

### Optional: use MySQL

1. Create a MySQL database and run `sql/schema.sql`.
2. Copy `.env.example` to `.env`.
3. Add your local MySQL connection values to `.env`.
4. Load the environment variables into your shell/session before running the CLI with `--mysql`.

```bash
python -m src.cli --xml examples/sample_clients.xml --mysql
```

Never commit real credentials or a populated `.env` file.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Example normalized record

```json
{
  "client_id": "C1001",
  "name": "Asha Rao",
  "email": "asha@example.com",
  "phone": "+91-9000000001",
  "created_at": "2026-01-15",
  "source": "xml_import"
}
```

## Example reconciliation result

The sample data intentionally includes an email mismatch and a client ID that is absent from the reference CSV. The reconciliation report identifies these differences rather than silently treating the records as identical.

## Notes and scope

This is a portfolio/demo implementation intended to show XML processing, data validation, JSON transformation, SQL-backed reference lookup, and reconciliation logic. The MySQL mode expects a locally configured database. No production deployment, external client integration, or performance benchmark is claimed.

## Author

**Siddhi Gauns**  
GitHub: [@siddhigauns0110-svg](https://github.com/siddhigauns0110-svg)
