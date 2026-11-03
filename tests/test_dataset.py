"""Offline integrity and scenario checks. SQL Server checks are documented separately."""

import csv
import hashlib
import importlib.util
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("generate_data", ROOT / "scripts" / "generate_data.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def load_csv():
    result = {}
    for table in generator.TABLES:
        with (ROOT / "data" / f"{table}.csv").open(newline="", encoding="utf-8") as handle:
            result[table] = list(csv.DictReader(handle))
    return result


def scenario_results():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    for table, rows in generator.build_data().items():
        columns = generator.TABLES[table]
        numeric = {
            col for row in rows for col, value in row.items()
            if isinstance(value, (int, Decimal))
        }
        definitions = ", ".join(f"{c} {'NUMERIC' if c in numeric else 'TEXT'}" for c in columns)
        connection.execute(f"CREATE TABLE {table} ({definitions})")
        connection.executemany(
            f"INSERT INTO {table} VALUES ({', '.join('?' for _ in columns)})",
            [[None if row[col] is None else generator.text(row[col]) for col in columns]
             for row in rows],
        )
    results = {}
    for path in sorted((ROOT / "sql" / "scenarios").glob("*.sql")):
        query = path.read_text(encoding="utf-8").replace("dbo.", "")
        results[path.stem] = [
            {key: round(value, 2) if isinstance(value, float) else value
             for key, value in dict(row).items()}
            for row in connection.execute(query)
        ]
    connection.close()
    return results


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_csv()
        cls.results = scenario_results()

    def test_exactly_seven_tables_and_manifest_hashes(self):
        manifest = json.loads((ROOT / "data" / "manifest.json").read_text())
        self.assertEqual(len(self.data), 7)
        for table, rows in self.data.items():
            self.assertEqual(list(rows[0]), generator.TABLES[table])
            self.assertEqual(len(rows), manifest["tables"][table]["rows"])
            path = ROOT / "data" / f"{table}.csv"
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                             manifest["tables"][table]["sha256"])
        schema = (ROOT / "sql" / "01_schema.sql").read_text()
        self.assertEqual(set(re.findall(r"CREATE TABLE dbo\.(\w+)", schema)), set(self.data))

    def test_reproducible_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_data.py"),
                            "--output", directory], check=True, capture_output=True)
            for relative in [Path("sql") / "02_seed.sql", Path("data") / "manifest.json"] + [
                Path("data") / f"{table}.csv" for table in self.data
            ]:
                self.assertEqual((Path(directory) / relative).read_bytes(),
                                 (ROOT / relative).read_bytes(), str(relative))

    def test_all_column_types_are_mirroring_safe(self):
        schema = (ROOT / "sql" / "01_schema.sql").read_text()
        tables = re.findall(r"CREATE TABLE dbo\.(\w+) \((.*?)\n    \);", schema, re.DOTALL)
        self.assertEqual(len(tables), 7)
        for table, body in tables:
            columns = re.findall(
                r"^\s*(\w+)\s+(\w+)(?:\(([^)]+)\))?\s+(?:NOT NULL|NULL)",
                body, re.MULTILINE,
            )
            self.assertEqual([column for column, _, _ in columns], generator.TABLES[table])
            self.assertEqual(columns[0][1:], ("int", ""))
            for column, kind, arguments in columns:
                with self.subTest(table=table, column=column):
                    self.assertIn(kind, {"int", "date", "char", "varchar", "nvarchar",
                                         "decimal", "datetime2"})
                    if kind in {"char", "varchar", "nvarchar"}:
                        self.assertTrue(arguments.isdigit(), "Use bounded text, not MAX.")
                        self.assertGreater(int(arguments), 0)
                    elif kind == "decimal":
                        self.assertEqual(arguments.replace(" ", ""), "12,2")
                    elif kind == "datetime2":
                        self.assertTrue(arguments.isdigit(), "Specify precision explicitly.")
                        self.assertIn(int(arguments), range(7), "Avoid precision loss in Delta.")
                    else:
                        self.assertEqual(arguments, "")

    def test_keys_and_referential_integrity(self):
        primary_keys = {}
        for table, rows in self.data.items():
            key = generator.TABLES[table][0]
            values = [row[key] for row in rows]
            self.assertEqual(len(values), len(set(values)), table)
            primary_keys[table] = set(values)
        references = {
            "Subscriptions": {"DealershipID": "Dealerships", "ProductID": "Products"},
            "UsageRecords": {"SubscriptionID": "Subscriptions"},
            "Invoices": {"DealershipID": "Dealerships"},
            "InvoiceLines": {"InvoiceID": "Invoices", "SubscriptionID": "Subscriptions"},
            "Payments": {"InvoiceID": "Invoices"},
        }
        for table, columns in references.items():
            for row in self.data[table]:
                for column, target in columns.items():
                    self.assertIn(row[column], primary_keys[target])
        for table, columns in {
            "UsageRecords": ("SubscriptionID", "UsageMonth"),
            "Invoices": ("DealershipID", "BillingMonth"),
        }.items():
            keys = [tuple(row[c] for c in columns) for row in self.data[table]]
            self.assertEqual(len(keys), len(set(keys)))

    def test_financial_reconciliation_and_grain(self):
        totals, collections = defaultdict(Decimal), defaultdict(Decimal)
        invoices = {row["InvoiceID"]: row for row in self.data["Invoices"]}
        subscriptions = {row["SubscriptionID"]: row for row in self.data["Subscriptions"]}
        for row in self.data["InvoiceLines"]:
            amount = Decimal(row["LineAmount"])
            self.assertEqual(amount, int(row["Quantity"]) * Decimal(row["UnitPrice"]))
            totals[row["InvoiceID"]] += amount
            invoice, subscription = invoices[row["InvoiceID"]], subscriptions[row["SubscriptionID"]]
            self.assertEqual(invoice["DealershipID"], subscription["DealershipID"])
            self.assertEqual(invoice["BillingMonth"], row["ServiceMonth"])
        for row in self.data["Payments"]:
            self.assertLessEqual(row["PaymentDate"], generator.AS_OF.isoformat())
            self.assertGreaterEqual(row["PaymentDate"], invoices[row["InvoiceID"]]["InvoiceDate"])
            if row["PaymentStatus"] == "Succeeded":
                self.assertEqual(row["FailureCode"], "")
                collections[row["InvoiceID"]] += Decimal(row["Amount"])
            else:
                self.assertTrue(row["FailureCode"])
        for invoice_id, row in invoices.items():
            self.assertEqual(totals[invoice_id], Decimal(row["TotalAmount"]))
            self.assertLessEqual(collections[invoice_id], totals[invoice_id])

    def test_planted_anomalies(self):
        result = self.results
        self.assertEqual(result["03_duplicate_subscriptions"][0]["ActiveContracts"], 2)
        self.assertEqual(result["03_duplicate_subscriptions"][0]["SuspectedExcessMRR"], 299)
        self.assertEqual(result["04_post_cancellation_billing"][0]["BilledAfterEnd"], 398)
        self.assertEqual(result["05_usage_spike"][0]["OctoberQuantity"], 2400)
        self.assertEqual(result["06_deep_discount"][0]["MonthlyListGap"], 300)
        self.assertEqual(result["07_rate_overcharge"][0]["Overcharge"], 500)
        self.assertEqual(result["08_unbilled_usage"][0]["UnbilledOverage"], 4500)
        self.assertEqual(result["09_failed_payment_attempts"][0]["FailedAttempts"], 6)
        self.assertEqual(result["09_failed_payment_attempts"][0]["AffectedInvoices"], 2)
        mrr = result["10_contract_mrr_change"]
        self.assertEqual(mrr[0]["ContractMRR"] - mrr[1]["ContractMRR"], 499)
        self.assertEqual(result["11_service_credits"][0]["CreditAmount"], -300)
        self.assertEqual(len(result["12_cross_sell"]), 13)

    def test_all_twelve_scenarios_match_expected_results(self):
        expected = json.loads((ROOT / "data" / "expected_results.json").read_text())
        self.assertEqual(len(self.results), 12)
        self.assertEqual(self.results, expected)

    def test_revenue_and_ar_independently(self):
        october_lines = [r for r in self.data["InvoiceLines"] if r["ServiceMonth"] == "2026-10-01"]
        expected_billed = sum(Decimal(r["LineAmount"]) for r in october_lines)
        actual_billed = sum(Decimal(str(r["NetBilled"]))
                            for r in self.results["01_october_billing"])
        self.assertEqual(expected_billed, actual_billed)
        succeeded = defaultdict(Decimal)
        for payment in self.data["Payments"]:
            if payment["PaymentStatus"] == "Succeeded":
                succeeded[payment["InvoiceID"]] += Decimal(payment["Amount"])
        overdue = sum(
            Decimal(i["TotalAmount"]) - succeeded[i["InvoiceID"]]
            for i in self.data["Invoices"]
            if i["DueDate"] < generator.AS_OF.isoformat()
        )
        self.assertEqual(overdue, sum(Decimal(str(r["OverdueBalance"]))
                                     for r in self.results["02_overdue_receivables"]))

    def test_dax_references_match_supplied_schema(self):
        dax = (ROOT / "semantic-model" / "measures.dax").read_text()
        measures = set(re.findall(r"MEASURE '(\w+)'\[([^\]]+)\]", dax))
        for table, field in re.findall(r"'(\w+)'\[([^\]]+)\]", dax):
            self.assertIn(table, generator.TABLES)
            self.assertTrue(field in generator.TABLES[table] or (table, field) in measures,
                            f"Unknown DAX reference: {table}[{field}]")


if __name__ == "__main__":
    unittest.main()
