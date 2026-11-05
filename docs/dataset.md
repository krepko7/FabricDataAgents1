# Fictional dealership billing data

All data is synthetic, including dealership names, subscriptions, amounts, and payment attempts. Billing email addresses use the reserved `.example` domain. Product names and prices are for illustration, not verified information about Dealership.

The files contain column headers and comma-separated UTF-8 data. Dates use `yyyy-MM-dd`; `RecordedAt` uses an ISO date/time; decimals use a period. Empty `EndDate` and `FailureCode` cells mean no value. Data covers January-October 2026, with a fixed **November 3, 2026** reporting date and USD currency.

## Tables and grain

| File / table | Grain | Key columns and important fields |
|---|---|---|
| `Dealerships.csv` / `dealerships` | One customer account | `DealershipID`, `DealershipName`, `DealerGroup`, `City`, `StateCode`, `Region`, `AccountStatus`, `JoinedDate`, `BillingEmail`, `PaymentTermsDays` |
| `Products.csv` / `products` | One catalog service | `ProductID`, `ProductCode`, `ProductName`, `Category`, `MonthlyListPrice`, `IncludedUnits`, `OverageUnitPrice`, `UsageUnit` |
| `Subscriptions.csv` / `subscriptions` | One customer/product contract | `SubscriptionID`, `DealershipID`, `ProductID`, `StartDate`, `EndDate`, `SubscriptionStatus`, `MonthlyRate`, `IncludedUnits`, `OverageUnitPrice`, `ContractReference` |
| `UsageRecords.csv` / `usagerecords` | One subscription/month settlement | `UsageRecordID`, `SubscriptionID`, `UsageMonth`, `Quantity`, `RecordedAt` |
| `Invoices.csv` / `invoices` | One customer/month invoice | `InvoiceID`, `InvoiceNumber`, `DealershipID`, `BillingMonth`, `InvoiceDate`, `DueDate`, `CurrencyCode`, `InvoiceStatus`, `TotalAmount` |
| `InvoiceLines.csv` / `invoicelines` | One charge or credit on an invoice | `InvoiceLineID`, `InvoiceID`, `SubscriptionID`, `ServiceMonth`, `LineType`, `Quantity`, `UnitPrice`, `LineAmount`, `ReasonCode` |
| `Payments.csv` / `payments` | One payment attempt against an invoice | `PaymentID`, `InvoiceID`, `PaymentDate`, `Amount`, `PaymentStatus`, `PaymentMethod`, `FailureCode`, `ProcessorReference` |

The original CSVs are normalized operational data, not a pre-built dimensional model. They contain no SQL types or enforced constraints: loading them into Delta tables infers types and does not create database primary or foreign keys. Define relationships in the semantic model.

## Types to check after loading

| Columns | Intended interpretation |
|---|---|
| All `...ID`, `Quantity`, `IncludedUnits`, `PaymentTermsDays` | Whole number; matching relationship keys must have the same type |
| `...Date`, `BillingMonth`, `ServiceMonth`, `UsageMonth` | Date; blanks in `EndDate` are null |
| `RecordedAt` | Date/time, interpreted as UTC |
| `MonthlyListPrice`, `MonthlyRate`, `OverageUnitPrice`, `TotalAmount`, `UnitPrice`, `LineAmount`, `Amount` | Numeric amounts; USD, with two decimal places |
| Names, codes, status, references, email, reason, city, region and state | Text; blanks in `FailureCode` are null |

The Lakehouse **Load to tables** dialog does not offer a custom column schema. Inspect the resulting table types before modeling. CSV inference can produce text or floating-point numbers; for example, `0.25` must be numeric, not text. For this demonstration, check numeric totals to the cent. Floating point isn't a substitute for fixed-precision currency in production. The [workshop troubleshooting section](workshop.md#troubleshooting) describes a no-code Dataflow Gen2 option if types aren't suitable.

## Catalog

| Service | List price/month | Included units | Overage price |
|---|---:|---:|---:|
| Dealer Website | $199 | N/A | N/A |
| Auction Access | $149 | 5 auctions | $15/auction |
| Vehicle Book Values | $89 | 100 lookups | $0.25/lookup |
| Dealer CRM | $299 | N/A | N/A |
| Dealer Management System | $499 | N/A | N/A |
| AutoCheck Reports (demo) | $99 | 25 reports | $2/report |
| Carfax Reports (demo) | $149 | 50 reports | $10/report |

The negotiated subscription rate can differ from list price. The `Quantity` in usage is total units, including the allowance; on a Usage invoice line it is billed **excess** units. A Credit line is negative.

## Business definitions

- **Entitled on a date:** the subscription has started and its `EndDate` is blank or on/after that date. `EndDate` is inclusive; `SubscriptionStatus` is current, not a historical snapshot.
- **Net billed:** signed issued invoice lines by service month. It's not cash or GAAP revenue recognition.
- **Contract MRR:** negotiated recurring subscription rates for contracts entitled on the snapshot date. It excludes usage, credits, and billed-price mistakes.
- **Cash collected:** successful payments only; failed rows are attempts, not cash.
- **Outstanding:** invoice total minus successful payments through the reporting date. **Overdue:** positive outstanding balance with due date before November 3, 2026.
- **Expected overage:** units above the contract allowance times the contract overage price, calculated per subscription/month. **Unbilled overage** compares this with actual Usage lines for the same subscription/month.

Don't add invoice totals after joining invoice lines or payment attempts: this repeats header totals. Failed payment retries can also repeat the same attempted amount. The data doesn't allocate invoice-level payments to products.

## Planted review candidates

The data includes a duplicate contract, charges after cancellation, extreme usage, unbilled usage, a deep discount, an overcharge, failed payment retries, a partial payment, a suspended subscription, and a service credit. See the [12 questions and answer key](demo-scenarios.md). These examples are review candidates, not proof of wrongdoing or a real customer problem.
