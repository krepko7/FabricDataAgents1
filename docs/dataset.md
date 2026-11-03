# Synthetic dealership billing dataset

## Design and scope

This is a fictional billing application inspired by the requested Nowcom demo, not extracted or reverse-engineered customer data. All accounts use reserved `.example` email addresses. Pricing and product names are illustrative. No payment-card numbers, credentials, VINs, or real contact records are included.

The **seven tables are OLTP entities**, with integer primary keys, enforced foreign keys, unique business references, checks, and operational indexes. The normalized invoice header/detail structure is preserved. Usage is stored as a monthly meter settlement transaction, not one row per API call and not a dimensional warehouse fact. A larger production design would likely separate plans, contract amendments, tax, allocations, dunning, and event-level usage; those are deliberately out of scope.

## Fabric Mirroring column compatibility

All **59 columns across the seven tables** use source types supported by Fabric Mirroring from Azure SQL Database and SQL Server. No column conversion or removal is needed:

| SQL source type used | Purpose | Mirroring consideration |
|---|---|---|
| `int` | All primary/foreign keys, quantities, and terms | All seven primary keys are integers, avoiding unsupported key types and character-key collation issues. |
| `char(2)`, `char(3)` | State and currency codes | Bounded character data. |
| `varchar(n)` | Codes, statuses, and references | Bounded character data; no legacy text or MAX columns. |
| `nvarchar(n)` | Dealer/product names, groups, and cities | Supported Unicode source text; replicated/endpoint representations need not preserve the source SQL type name. |
| `decimal(12,2)` | Currency amounts and rates | Exact values; no floating-point currency conversions. |
| `date` | Billing periods, entitlement dates, and payment dates | Calendar dates without a time-zone or fractional-second conversion. |
| `datetime2(0)` | `UsageRecords.RecordedAt` | Explicit zero fractional digits, safely within Delta's six-digit precision limit; timestamps are interpreted as UTC. |

There are **no computed columns**, user-defined/CLR types, `rowversion`/`timestamp`, `xml`, `sql_variant`, spatial types, `hierarchyid`, legacy `text`/`ntext`/`image`, native `json`/`vector`, or unbounded LOB columns. No clustered columnstore, temporal history, ledger history, in-memory, graph, or external tables are used.

Don't change `RecordedAt` to an unqualified `datetime2`: its SQL default is precision 7, and mirroring trims the seventh fractional digit. Precision-7 temporal key types also have key eligibility restrictions. The demo deliberately avoids both precision loss and unsupported columns being omitted.

`sql\03_validate.sql` checks actual `sys.columns`/`sys.types` metadata before reconciling data and fails with the offending column names. Its conservative demo allowlist accepts integers/dates, bounded text, `decimal(12,2)`, and explicit `datetime2` precision 0-6; **it is not the full list of all types Fabric supports**. Offline schema tests prevent accidental unsupported types, implicit timestamp precision, or unparsed columns in source changes.

Reviewed against Microsoft's [Azure SQL mirroring limitations](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database-limitations) and [SQL Server mirroring limitations](https://learn.microsoft.com/en-us/fabric/mirroring/sql-server-limitations) on 2026-11-03. Type compatibility alone doesn't establish source eligibility: this workshop still targets **Azure SQL Database**. Mirroring a self-managed SQL Server instead requires its version-specific setup, permissions, networking, and CDC/replication prerequisites; LocalDB execution isn't proof of mirroring eligibility.

## Data dictionary

### Dealerships - one customer billing account

| Columns | Meaning |
|---|---|
| `DealershipID` | Integer primary key, 1-24 |
| `DealershipName`, `DealerGroup` | Fictional customer and group labels |
| `City`, `StateCode`, `Region` | Six US locations and four reporting regions |
| `AccountStatus` | Customer account status; all seeded accounts are Active, even if an individual subscription ended |
| `JoinedDate` | Account creation date, not a subscription start |
| `BillingEmail` | Unique reserved-domain address |
| `PaymentTermsDays` | 15 days for all seeded accounts |

### Products - one catalog service

| Code | Illustrative service | Monthly list USD | Included units/month | Overage USD/unit |
|---|---|---:|---:|---:|
| WEB | Dealer Website | 199 | 0 | 0 |
| AUCTION | Auction Access | 149 | 5 auctions | 15 |
| BOOK | Vehicle Book Values | 89 | 100 lookups | 0.25 |
| CRM | Dealer CRM | 299 | 0 | 0 |
| DMS | Dealer Management System | 499 | 0 | 0 |
| AUTOCHECK | AutoCheck Reports (demo) | 99 | 25 reports | 2 |
| CARFAX | Carfax Reports (demo) | 149 | 50 reports | 10 |

`ProductID` is the primary key; `ProductCode` is unique. `ProductName`, `Category`, `MonthlyListPrice`, `IncludedUnits`, `OverageUnitPrice`, and `UsageUnit` describe the offer. Product list pricing isn't an invoice charge or the customer's negotiated contract price.

### Subscriptions - one customer/product contract

| Columns | Meaning |
|---|---|
| `SubscriptionID` | Explicit integer key; standard IDs = dealership ID * 100 + product ID |
| `DealershipID`, `ProductID` | Foreign keys to customer and catalog |
| `StartDate`, `EndDate` | Inclusive entitlement dates; blank end means open-ended |
| `SubscriptionStatus` | Current Active, Cancelled, or Suspended state, not historical monthly status |
| `MonthlyRate` | Negotiated base monthly fee used for contractual MRR |
| `IncludedUnits`, `OverageUnitPrice` | Contract terms; seeded as copies of the original catalog terms |
| `ContractReference` | Unique external-style contract reference |

Overlapping customer/product contracts are intentionally not prohibited: Maple Grove Auto has a second CRM contract, ID `754`, from September. Real systems may have valid multiple contracts; treat the overlap as a review candidate, not proof of wrongdoing.

### UsageRecords - one subscription/month meter settlement

`UsageRecordID` is the key; `(SubscriptionID, UsageMonth)` is unique. `Quantity` is the month's **total** usage, including the allowance. `RecordedAt` is the meter posting timestamp in UTC. Only metered, entitled subscriptions have usage records.

Expected overage = `MAX(0, Quantity - Subscriptions.IncludedUnits) * Subscriptions.OverageUnitPrice`.

### Invoices - one dealership/month invoice header

`InvoiceID` and unique `InvoiceNumber` identify the invoice. `DealershipID` is a foreign key. `(DealershipID, BillingMonth)` is unique. `BillingMonth` is the first day of the service month; `InvoiceDate` is month-end and `DueDate` is 15 days later.

`CurrencyCode` is USD. `InvoiceStatus` supports Issued and Void; all seed invoices are Issued. `TotalAmount` is a stored operational header total that reconciles to its lines. There is deliberately **no mutable Paid flag**: settlement derives from successful payments.

### InvoiceLines - one billed charge or credit

`InvoiceLineID` is the key. `InvoiceID` links the header and `SubscriptionID` links the contract. The invoice customer always matches the subscription customer.

`ServiceMonth` identifies the billed service period. `LineType` is Recurring, Usage, or Credit. `Quantity * UnitPrice = LineAmount`; recurring and credit quantities are 1, usage quantities are billable excess units. Credits have negative prices/amounts. `ReasonCode` identifies MonthlyFee, MeteredOverage, or ServiceCredit.

There is no redundant ProductID: reach the product through the contract. Do **not** sum invoice header totals after joining the lines; that multiplies the totals.

### Payments - one processor payment attempt

`PaymentID` is the key; `InvoiceID` is a foreign key. `PaymentDate`, `Amount`, and `PaymentMethod` describe the attempt; seeded methods are ACH. `ProcessorReference` is unique.

`PaymentStatus` is Succeeded or Failed; failed attempts have `FailureCode = InsufficientFunds`. A failed attempt's positive Amount is the **attempted** amount, never collected cash. Coastal Bend Auto has three retries on each of two invoices. Prairie View Cars has two successful installments for its October invoice. Blue Canyon Auto's September invoice is half-paid.

## Billing and reporting rules

| Concept | Definition |
|---|---|
| Reporting date | 2026-11-03; no `GETDATE()`/`TODAY()` in baseline answers |
| Service coverage | January 1 through October 31, 2026; no November invoices |
| Monthly billing | In arrears, no proration, one customer invoice per month |
| Contract terms | Unchanged within each seeded contract; no rate/allowance version history |
| Entitled on date D | `StartDate <= D AND (EndDate IS NULL OR EndDate >= D)` |
| Contract MRR | Sum entitled negotiated monthly base rates on a snapshot date; exclude usage, credits, and incorrect billing |
| Net billed revenue | Signed issued invoice lines by service month; demo billing metric, **not GAAP revenue recognition** |
| Collected cash | Succeeded payments dated on/before reporting date |
| Outstanding | Issued invoice total less successful payments, evaluated once per invoice |
| Overdue | Positive outstanding balance with `DueDate < reporting date` |
| Not yet due | October invoices are due November 15 and are **not overdue** on November 3 |
| Credit | Negative invoice line, not a payment/refund |
| Growth opportunity | List-price opportunity only, not pipeline, booked revenue, or predicted conversion |

The post-cancellation and pricing defects are intentional **business-rule anomalies**, not broken referential integrity or unbalanced books. The source schema does not enforce every cross-table business rule; reconciliation checks protect the supplied dataset.

## Loading

The recommended path is `scripts\Load-Demo.ps1`, as shown in the root README. Run against an empty, dedicated **Azure SQL Database**. This workshop uses Azure SQL as the source, not a Fabric SQL database, SQL Server traditional database mirroring, or Azure SQL Managed Instance.

Load order is Dealerships, Products, Subscriptions, UsageRecords, Invoices, InvoiceLines, Payments. The generated `sql\02_seed.sql` respects foreign keys and inserts at most 500 rows per INSERT. Its single transaction rolls back on any error and refuses to seed nonempty demo tables. Schema creation is also transactional and refuses existing demo objects.

The schema and seed are separate operations: if seeding fails, empty schema tables remain, and the seed can be retried after resolving the error. The full loader deliberately refuses to rerun schema creation; use the seed script alone only when all seven tables are confirmed empty.

CSVs in `data\` are an optional alternative for customer-preferred import tools. They are UTF-8, comma-delimited, headered, LF-terminated, with ISO dates, decimal-point currency, and blank nullable fields. **Do not import CSVs after running the seed SQL.** Use the supplied typed schema and map blank `EndDate` and `FailureCode` to SQL NULL. No CSV import tool is assumed or required.

Every key is explicit, not IDENTITY. For new source transactions use unique IDs; `sql\04_live_payment.sql` demonstrates this under locking.

## Rebuilding and extending

```powershell
python .\scripts\generate_data.py
python -m unittest discover -s tests -v
```

The generator is deterministic and uses exact Decimal arithmetic. It writes seven CSVs, `data\manifest.json`, and `sql\02_seed.sql`; no random seed or package install is needed. It doesn't overwrite the hand-maintained answer key `data\expected_results.json`. If you change dates, prices, or fixtures, intentionally review and update SQL scenarios, DAX, documentation, tests, and the answer key together.

## Validation

Offline tests use a temporary in-memory SQLite database for the SELECT-only scenarios plus independent Decimal reconciliation. They do **not** prove T-SQL DDL or DAX compatibility. To validate actual SQL execution, first load an isolated SQL Server/Azure SQL test database and run:

```powershell
$env:NOWCOM_TEST_SQLSERVER = '<server>.database.windows.net'
$env:NOWCOM_TEST_DATABASE = 'NowcomBillingDemo'
$env:NOWCOM_TEST_ENTRA = '1'
python -m unittest discover -s tests -v
```

For an already loaded local SQL Server instance with Windows authentication, omit `NOWCOM_TEST_ENTRA`. Integration tests run reconciliation and all 12 T-SQL queries, compare SQL Server JSON output to the answer key, verify reload refusal, and exercise the live payment inside a rolled-back transaction. Use a disposable baseline database, not production or a shared active workshop database. They don't create or delete databases and leave the baseline data intact. They require Microsoft's ODBC `sqlcmd` CLI with `-y 0` support.

`sql\03_validate.sql` can also be run directly on Azure SQL. Verify the seven row counts against `data\manifest.json`, not the preview UI's first 1,000 rows. The seed/queries have been exercised with SQL Server LocalDB; Azure SQL/Fabric connectivity, permissions, replication, and DAX still require the workshop's cloud checkpoints.

## Reset and cleanup

No automatic destructive reset is provided. For another baseline rehearsal use a new dedicated database and a new mirrored item, or have the resource owner explicitly approve disposal/recreation of the prior demo resources. Don't delete customer resources, disable shared tenant settings, or drop production tables. Stop or remove only dedicated resources you own when the workshop ends, following organizational retention and cost policies.
