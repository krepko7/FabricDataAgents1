"""Rebuild the fictional Nowcom workshop data using only the Python standard library."""

import argparse
import calendar
import csv
import hashlib
import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 3)
CENT = Decimal("0.01")
TABLES = {
    "Dealerships": (
        "DealershipID DealershipName DealerGroup City StateCode Region AccountStatus "
        "JoinedDate BillingEmail PaymentTermsDays"
    ).split(),
    "Products": (
        "ProductID ProductCode ProductName Category MonthlyListPrice IncludedUnits "
        "OverageUnitPrice UsageUnit"
    ).split(),
    "Subscriptions": (
        "SubscriptionID DealershipID ProductID StartDate EndDate SubscriptionStatus "
        "MonthlyRate IncludedUnits OverageUnitPrice ContractReference"
    ).split(),
    "UsageRecords": "UsageRecordID SubscriptionID UsageMonth Quantity RecordedAt".split(),
    "Invoices": (
        "InvoiceID InvoiceNumber DealershipID BillingMonth InvoiceDate DueDate "
        "CurrencyCode InvoiceStatus TotalAmount"
    ).split(),
    "InvoiceLines": (
        "InvoiceLineID InvoiceID SubscriptionID ServiceMonth LineType Quantity "
        "UnitPrice LineAmount ReasonCode"
    ).split(),
    "Payments": (
        "PaymentID InvoiceID PaymentDate Amount PaymentStatus PaymentMethod "
        "FailureCode ProcessorReference"
    ).split(),
}


def money(value):
    return Decimal(str(value)).quantize(CENT)


def build_data():
    data = {table: [] for table in TABLES}

    def add(table, *values):
        assert len(values) == len(TABLES[table])
        row = dict(zip(TABLES[table], values))
        data[table].append(row)
        return row

    names = [
        "Cedar Ridge Motors", "Harbor Point Auto", "Prairie View Cars",
        "Desert Mesa Motors", "Lakefront Auto Mall", "Summit Trail Motors",
        "Maple Grove Auto", "Riverbend Car Center", "Sunset Valley Motors",
        "Blue Canyon Auto", "Oak Hollow Motors", "Pinecrest Auto",
        "Silver Creek Cars", "Red Rock Auto", "Willow Brook Motors",
        "Golden Plains Auto", "Aspen Ridge Motors", "Coastal Bend Auto",
        "Cypress Lane Cars", "Stonebridge Motors", "Meadow Park Auto",
        "Clearwater Car Center", "Juniper Hill Motors", "Northstar Auto",
    ]
    locations = [
        ("Irvine", "CA", "West"), ("Phoenix", "AZ", "West"),
        ("Dallas", "TX", "South"), ("Tampa", "FL", "South"),
        ("Columbus", "OH", "Midwest"), ("Albany", "NY", "Northeast"),
    ]
    for dealer_id, name in enumerate(names, 1):
        city, state, region = locations[(dealer_id - 1) % len(locations)]
        add("Dealerships", dealer_id, name, f"Demo Group {(dealer_id - 1) // 6 + 1}",
            city, state, region, "Active", date(2024, 1, 1),
            f"billing{dealer_id:02}@dealership.example", 15)

    catalog = [
        (1, "WEB", "Dealer Website", "Digital retail", 199, 0, 0, "None"),
        (2, "AUCTION", "Auction Access", "Auctions", 149, 5, 15, "Auctions"),
        (3, "BOOK", "Vehicle Book Values", "Valuations", 89, 100, ".25", "Lookups"),
        (4, "CRM", "Dealer CRM", "CRM", 299, 0, 0, "None"),
        (5, "DMS", "Dealer Management System", "DMS", 499, 0, 0, "None"),
        (6, "AUTOCHECK", "AutoCheck Reports (demo)", "Vehicle history", 99, 25, 2, "Reports"),
        (7, "CARFAX", "Carfax Reports (demo)", "Vehicle history", 149, 50, 10, "Reports"),
    ]
    for pid, code, name, category, price, included, overage, unit in catalog:
        add("Products", pid, code, name, category, money(price), included, money(overage), unit)

    def add_subscription(dealer_id, pid, start=date(2026, 1, 1), duplicate=False):
        product = data["Products"][pid - 1]
        sid = dealer_id * 100 + pid + (50 if duplicate else 0)
        end, status = None, "Active"
        if (dealer_id, pid) == (12, 1):
            end, status = date(2026, 8, 31), "Cancelled"
        elif (dealer_id, pid) == (22, 4):
            end, status = date(2026, 6, 30), "Cancelled"
        elif (dealer_id, pid) == (20, 5):
            end, status = date(2026, 9, 30), "Suspended"
        rate = money(199) if (dealer_id, pid) == (6, 5) else product["MonthlyListPrice"]
        return add("Subscriptions", sid, dealer_id, pid, start, end, status, rate,
                   product["IncludedUnits"], product["OverageUnitPrice"], f"DEMO-{sid:05}")

    for dealer_id in range(1, 25):
        pids = {1, 4, 5, 7}
        if dealer_id != 24:
            if dealer_id % 2 == 0:
                pids.add(2)
            if dealer_id % 3 == 0:
                pids.add(3)
            if dealer_id % 2 == 1:
                pids.add(6)
        for pid in sorted(pids):
            add_subscription(dealer_id, pid)
    add_subscription(7, 4, date(2026, 9, 1), duplicate=True)

    def add_line(invoice_id, sub, month, line_type, quantity, unit_price, reason):
        return add("InvoiceLines", len(data["InvoiceLines"]) + 1, invoice_id,
                   sub["SubscriptionID"], month, line_type, quantity, unit_price,
                   money(quantity * unit_price), reason)

    for month_number in range(1, 11):
        month = date(2026, month_number, 1)
        end_of_month = date(2026, month_number, calendar.monthrange(2026, month_number)[1])
        invoice_date = end_of_month
        for dealer in data["Dealerships"]:
            did = dealer["DealershipID"]
            invoice_id = month_number * 100 + did
            invoice = add("Invoices", invoice_id, f"INV-2026{month_number:02}-{did:03}",
                          did, month, invoice_date, invoice_date + timedelta(days=15),
                          "USD", "Issued", money(0))
            for sub in data["Subscriptions"]:
                if sub["DealershipID"] != did or sub["StartDate"] > month:
                    continue
                entitled = sub["EndDate"] is None or sub["EndDate"] >= month
                # This cancelled subscription intentionally keeps being billed.
                stale_billing = (did, sub["ProductID"]) == (12, 1) and not entitled
                if not entitled and not stale_billing:
                    continue
                price = sub["MonthlyRate"]
                if (did, sub["ProductID"], month_number) == (11, 5, 10):
                    price = money(999)
                add_line(invoice_id, sub, month, "Recurring", 1, price, "MonthlyFee")

                if entitled and sub["OverageUnitPrice"] > 0:
                    included = sub["IncludedUnits"]
                    quantity = included + 10 + (did * 7 + month_number * 3) % 40
                    if (did, sub["ProductID"], month_number) == (9, 7, 10):
                        quantity = 2400
                    if (did, sub["ProductID"], month_number) == (15, 7, 10):
                        quantity = 500
                    add("UsageRecords", len(data["UsageRecords"]) + 1, sub["SubscriptionID"],
                        month, quantity, f"{end_of_month.isoformat()}T18:00:00")
                    if (did, sub["ProductID"], month_number) != (15, 7, 10):
                        add_line(invoice_id, sub, month, "Usage", quantity - included,
                                 sub["OverageUnitPrice"], "MeteredOverage")
                if (did, sub["ProductID"], month_number) == (16, 5, 9):
                    add_line(invoice_id, sub, month, "Credit", 1, money(-300), "ServiceCredit")
            invoice["TotalAmount"] = sum(
                (line["LineAmount"] for line in data["InvoiceLines"]
                 if line["InvoiceID"] == invoice_id), money(0)
            )

    def add_payment(invoice, when, amount, status="Succeeded", failure=None):
        payment_id = len(data["Payments"]) + 1
        add("Payments", payment_id, invoice["InvoiceID"], when, amount, status,
            "ACH", failure, f"DEMO-PAY-{payment_id:06}")

    for invoice in data["Invoices"]:
        did = invoice["DealershipID"]
        month_number = invoice["BillingMonth"].month
        paid_on = invoice["InvoiceDate"] + timedelta(days=1)
        if did == 4 and month_number >= 8:
            continue
        if did == 18 and month_number >= 9:
            for attempt in range(3):
                add_payment(invoice, paid_on + timedelta(days=attempt),
                            invoice["TotalAmount"], "Failed", "InsufficientFunds")
        elif did == 10 and month_number == 9:
            add_payment(invoice, paid_on, money(invoice["TotalAmount"] / 2))
        elif did == 3 and month_number == 10:
            first = money(invoice["TotalAmount"] / 2)
            add_payment(invoice, paid_on, first)
            add_payment(invoice, paid_on, invoice["TotalAmount"] - first)
        else:
            add_payment(invoice, paid_on, invoice["TotalAmount"])
    return data


def text(value):
    if value is None:
        return ""
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def sql_literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, Decimal)):
        return str(value)
    return "N'" + text(value).replace("'", "''") + "'"


def write_artifacts(output):
    data = build_data()
    csv_dir, sql_dir = output / "data", output / "sql"
    csv_dir.mkdir(parents=True, exist_ok=True)
    sql_dir.mkdir(parents=True, exist_ok=True)
    sql = [
        "-- Generated by scripts\\generate_data.py. Fictional data only.",
        "SET NOCOUNT ON;", "SET XACT_ABORT ON;", "BEGIN TRY", "BEGIN TRANSACTION;",
    ]
    for table in TABLES:
        sql.extend([
            f"IF EXISTS (SELECT 1 FROM dbo.{table})",
            "    THROW 50002, 'Seed requires all seven demo tables to be empty.', 1;",
        ])
    manifest = {"as_of_date": AS_OF.isoformat(), "currency": "USD",
                "billing_months": ["2026-01-01", "2026-10-01"], "tables": {}}
    for table, columns in TABLES.items():
        path = csv_dir / f"{table}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(columns)
            writer.writerows([text(row[col]) for col in columns] for row in data[table])
        manifest["tables"][table] = {
            "rows": len(data[table]),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for start in range(0, len(data[table]), 500):
            rows = data[table][start:start + 500]
            sql.append(f"INSERT INTO dbo.{table} ({', '.join(columns)}) VALUES")
            sql.append(",\n".join(
                "(" + ", ".join(sql_literal(row[col]) for col in columns) + ")" for row in rows
            ) + ";")
    sql.extend(["COMMIT;", "END TRY", "BEGIN CATCH",
                "IF @@TRANCOUNT > 0 ROLLBACK;", "THROW;", "END CATCH;", ""])
    (sql_dir / "02_seed.sql").write_text("\n".join(sql), encoding="utf-8", newline="\n")
    (csv_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print("Generated " + ", ".join(f"{t}={len(rows)}" for t, rows in data.items()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT,
                        help="Output root; defaults to the repository root.")
    write_artifacts(parser.parse_args().output)
