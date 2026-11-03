# Zero ETL to data insights with Fabric Data Agents

A hands-on Nowcom-themed workshop: load a fictional dealership billing application into **Azure SQL Database**, mirror its seven OLTP tables to Microsoft Fabric, build a semantic model, explore the SQL analytics endpoint, and ask a Fabric Data Agent 12 business questions.

**All dealerships, contracts, usage, invoices, payments, prices, and anomalies are synthetic.** The product categories are illustrative, not a verified Nowcom product catalog, commercial offer, or statement about Nowcom customers. AutoCheck and Carfax are referenced only as requested demo categories; no vendor integration or endorsement is implied.

## Start here

| Resource | Purpose |
|---|---|
| [Workshop agenda and labs](docs/workshop.md) | Three-hour facilitator/participant guide in the requested sequence |
| [Dataset and data dictionary](docs/dataset.md) | Seven-table transactional design, billing rules, and loading details |
| [Semantic model guide](docs/semantic-model.md) | Direct Lake setup, unambiguous relationships, measures, report pages |
| [12 demo questions and answer key](docs/demo-scenarios.md) | Prompts, expected answers, business actions, matching SQL |
| [Agent and model instructions](docs/agent-instructions.md) | Separate orchestration instructions and model-level Prep for AI guidance |
| [CSV files and manifest](data/) | Ready-made data, row counts, hashes, expected scenario results |
| [SQL scripts](sql/) | Schema, complete seed, source checks, optional live change, 12 queries |
| [DAX starter measures](semantic-model/measures.dax) | Query-scoped definitions to test, then persist in the semantic model |

## Load into Azure SQL Database

Use a **dedicated empty demo database**, not a customer production database. Choose a mirroring-supported tier: vCore-based, or DTU Standard S3/100 DTUs or higher; DTU Free/Basic and Standard below 100 DTUs aren't supported. Azure SQL and Fabric resources can incur charges.

From PowerShell in this repository, with `sqlcmd` installed and your Microsoft Entra database access configured:

```powershell
.\scripts\Load-Demo.ps1 -Server '<server>.database.windows.net' -Database 'NowcomBillingDemo'
```

The loader uses Entra authentication and encryption, runs `sql\01_schema.sql`, `sql\02_seed.sql`, and `sql\03_validate.sql`, and stops on errors. No secrets are stored. Alternatively, execute those three scripts in that order using SSMS or the VS Code MSSQL extension connected to the same Azure SQL database.

**Python is not required to load:** the complete seed SQL and CSVs are already included. The SQL route loads from local INSERT statements, so you don't need Blob Storage, SAS tokens, BULK INSERT permissions, or a pipeline. The scripts intentionally refuse to replace existing demo tables or reseed nonempty tables.

## Dataset at a glance

| Table | Rows | Transactional role |
|---|---:|---|
| Dealerships | 24 | Customer accounts and billing terms |
| Products | 7 | Service catalog and list pricing |
| Subscriptions | 127 | Customer contracts and negotiated rates |
| UsageRecords | 540 | Monthly meter settlement records |
| Invoices | 240 | Monthly customer invoice headers |
| InvoiceLines | 1,797 | Recurring fees, overages, and signed credits |
| Payments | 242 | Successful collections and failed payment attempts |

There are **2,977 rows**, January-October 2026 billing history, USD only, and a fixed reporting date of **November 3, 2026**. Keeping the clock fixed makes demos repeatable. There is no star schema, ETL pipeline, extra date table, or precomputed anomaly table.

The planted cases include duplicate CRM contracts, billing after cancellation, extreme vehicle-history usage, unbilled overages, deep discounts, a rate overcharge, failed collection retries, partial payment, suspended recurring revenue, and a service credit. October net billed revenue is **$66,728**; contract MRR is a separate **$29,956**.

## Rebuild and check locally

Python 3.10+ and the standard library are sufficient:

```powershell
python .\scripts\generate_data.py
python -m unittest discover -s tests -v
```

The tests cover deterministic regeneration, CSV hashes, key integrity, invoice reconciliation, planted anomalies, and all 12 reference query outputs. Optional SQL Server integration checks are described in [the dataset guide](docs/dataset.md#validation).

**Scope:** this repository contains the dataset and workshop assets. Loading the Azure SQL database, configuring mirroring, saving a semantic model, creating reports, and publishing a Data Agent are participant lab steps; no cloud resources are provisioned by these files. DAX definitions require validation in the participant's actual semantic model.
