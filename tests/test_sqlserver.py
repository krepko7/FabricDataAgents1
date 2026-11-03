"""Opt-in SQL Server scenario checks against an already loaded demo database."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    os.environ.get("NOWCOM_TEST_SQLSERVER") and os.environ.get("NOWCOM_TEST_DATABASE"),
    "Set NOWCOM_TEST_SQLSERVER and NOWCOM_TEST_DATABASE to a loaded demo database.",
)
class SqlServerTests(unittest.TestCase):
    def run_sql(self, query):
        auth = ["-G", "-N"] if os.environ.get("NOWCOM_TEST_ENTRA") == "1" else ["-E"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "query.sql"
            path.write_text("SET NOCOUNT ON;\n" + query, encoding="utf-8")
            result = subprocess.run(
                ["sqlcmd", "-S", os.environ["NOWCOM_TEST_SQLSERVER"],
                 "-d", os.environ["NOWCOM_TEST_DATABASE"], *auth,
                 "-b", "-y", "0", "-w", "65535", "-i", str(path)],
                capture_output=True, text=True,
            )
        if result.returncode:
            raise AssertionError(f"sqlcmd failed:\n{result.stdout}\n{result.stderr}")
        return result.stdout.strip()

    def test_scenario_results_on_sql_server(self):
        expected = json.loads((ROOT / "data" / "expected_results.json").read_text())
        for path in sorted((ROOT / "sql" / "scenarios").glob("*.sql")):
            with self.subTest(scenario=path.stem):
                query = path.read_text().strip().removesuffix(";") + "\nFOR JSON PATH;"
                self.assertEqual(json.loads(self.run_sql(query)), expected[path.stem])

    def test_reconciliation_on_sql_server(self):
        query = (ROOT / "sql" / "03_validate.sql").read_text()
        self.assertIn("PASS: source reconciliation", self.run_sql(query))

    def test_schema_and_seed_refuse_reload(self):
        for filename, message in [
            ("01_schema.sql", "Demo tables already exist"),
            ("02_seed.sql", "Seed requires all seven demo tables to be empty"),
        ]:
            with self.subTest(script=filename):
                with self.assertRaisesRegex(AssertionError, message):
                    self.run_sql((ROOT / "sql" / filename).read_text())
        self.test_reconciliation_on_sql_server()

    def test_live_payment_in_rolled_back_transaction(self):
        live = (ROOT / "sql" / "04_live_payment.sql").read_text()
        verification = """
IF (SELECT COUNT(*) FROM dbo.Payments) <> 243
    THROW 50030, 'Expected one new payment.', 1;
IF (SELECT Amount FROM dbo.Payments WHERE ProcessorReference = 'DEMO-LIVE-804') <> 1845
    THROW 50030, 'Expected live collection of 1845 USD.', 1;
DECLARE @Overdue decimal(12,2);
SELECT @Overdue = SUM(Balance) FROM (
    SELECT i.TotalAmount - COALESCE((
        SELECT SUM(p.Amount) FROM dbo.Payments p
        WHERE p.InvoiceID = i.InvoiceID AND p.PaymentStatus = 'Succeeded'
    ), 0) AS Balance FROM dbo.Invoices i
    WHERE i.DealershipID = 4 AND i.DueDate < '2026-11-03'
) balances;
IF @Overdue <> 1920
    THROW 50030, 'Expected remaining dealer overdue of 1920 USD.', 1;
ROLLBACK;
SELECT 'PASS: live payment rolled back' AS Result;
"""
        self.assertIn("PASS: live payment rolled back",
                      self.run_sql("BEGIN TRANSACTION;\n" + live + "\n" + verification))
        execute_live = "EXEC sys.sp_executesql N'" + live.replace("'", "''") + "';\n"
        with self.assertRaisesRegex(AssertionError, "This demo payment was already applied"):
            self.run_sql("BEGIN TRANSACTION;\n" + execute_live + execute_live)
        self.test_reconciliation_on_sql_server()


if __name__ == "__main__":
    unittest.main()
