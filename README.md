# From data to insights with Fabric Data Agents

Choose a file-upload or Azure SQL mirroring workshop using **fictional** Dealership-themed dealership billing data. Create a semantic model and explore the data with a Fabric Data Agent. The three-hour editions also call the published Data Agent from an MCP client.

**These are synthetic data and illustrative product names and prices, not real Dealership customers or verified Dealership offerings.** AutoCheck and Carfax are included as requested demo categories; no vendor integration or endorsement is implied.

## Choose your workshop

| Resource | Time | Data and scope |
|---|---|---|
| [**Workshop Express with file upload**](workshop-express/README.md) | 60-75 minutes | **Two CSVs and one relationship**; billing plus product lookup, Lakehouse upload, semantic model, Prep for AI, Data Agent instructions, and 12 copy-ready questions |
| [Workshop with file upload](docs/workshop.md) | 3 hours | Seven operational-style CSVs, model relationships, Data Agent, 12 questions, and MCP clients |
| [Workshop with mirroring](docs/workshop-mirroring.md) | 3 hours | Mirror seven tables from Azure SQL Database `dealership` on `kirbysqlserver2.database.windows.net`, then model, configure the agent, try 12 questions, and use MCP |

Express is a separate, consolidated resource; the original seven-table workshop remains unchanged. Start with [Workshop Express with file upload](workshop-express/README.md) for the quickest lab.

## Workshop with file upload agenda (3 hours)

| Time | Topic | Outcome |
|---|---|---|
| 00:00-00:15 | Introduction to Fabric | Understand the workspace, OneLake, Lakehouse, semantic model, and Data Agent |
| 00:15-00:30 | Create a workspace and Lakehouse | Create a capacity-backed workspace and workshop Lakehouse |
| 00:30-01:05 | Upload CSVs and create tables | Load seven CSVs as Lakehouse Delta tables and inspect their types |
| 01:05-01:35 | Create a semantic model | Define relationships and verify simple report results |
| 01:35-02:00 | Create and configure a Data Agent | Add the model, apply AI instructions, and publish the agent |
| 02:00-02:35 | Explore 12 business questions | Compare agent responses with the facilitator answer key |
| 02:35-02:55 | Connect the Data Agent as an MCP server | Discover and call the published agent from an MCP client |
| 02:55-03:00 | Wrap-up | Discuss results, permissions, and next steps |

Capacity provisioning and tenant approvals should be completed before the workshop.

## Workshop with mirroring agenda (3 hours)

| Time | Topic | Outcome |
|---|---|---|
| 00:00-00:15 | Introduction to Fabric and mirroring | Understand OneLake, managed replication, semantic meaning, and Data Agents |
| 00:15-00:30 | Workspace and source readiness | Confirm capacity, identity, network, permissions, and source eligibility |
| 00:30-01:05 | Configure Azure SQL Database mirroring | Select seven tables and verify initial replication and SQL endpoint availability |
| 01:05-01:35 | Create a semantic model | Define six relationships and verify report results |
| 01:35-02:00 | Create and configure a Data Agent | Add the model, apply AI instructions, and publish |
| 02:00-02:35 | Explore 12 business questions | Compare responses with the facilitator answer key |
| 02:35-02:55 | Connect the Data Agent as an MCP server | Discover and call the published agent from an MCP client |
| 02:55-03:00 | Wrap-up | Discuss replication, permissions, and next steps |

Use the [mirroring guide](docs/workshop-mirroring.md) for the supplied server/database and administrator prerequisites. Configure **one shared mirror** of `dealership`; don't create competing mirrors in each participant's workspace. The source schema and data haven't been verified live. This edition doesn't require CSV upload or a separate Lakehouse.

## Workshop resources

| Resource | Purpose |
|---|---|
| [Workshop agenda and step-by-step labs](docs/workshop.md) | Workspace, Lakehouse, CSV-to-table, semantic model, agent, and MCP walkthrough |
| [Workshop with mirroring](docs/workshop-mirroring.md) | Azure SQL Database connection, replication, mirrored-table semantic model, agent, and MCP walkthrough |
| [Data dictionary](docs/dataset.md) | Seven CSVs, column types, business definitions, and planted anomalies |
| [Semantic model guide](docs/semantic-model.md) | Relationships, type checks, and model limitations |
| [AI instructions](docs/agent-instructions.md) | Copy-ready Data Agent and semantic model Prep for AI guidance |
| [12 demo questions and answer key](docs/demo-scenarios.md) | Natural-language questions and facilitator checks |
| [MCP client guide](docs/mcp.md) | Publish the agent, connect from VS Code, and test its MCP tool |
| [Sample CSV files](data/) | The only files participants need to upload |

## Sample data

| CSV | Lakehouse table name | Rows | What it contains |
|---|---|---:|---|
| `Dealerships.csv` | `dealerships` | 24 | Fictional customer accounts |
| `Products.csv` | `products` | 7 | Service catalog |
| `Subscriptions.csv` | `subscriptions` | 127 | Customer contracts and prices |
| `UsageRecords.csv` | `usagerecords` | 540 | Monthly usage |
| `Invoices.csv` | `invoices` | 240 | Monthly invoice headers |
| `InvoiceLines.csv` | `invoicelines` | 1,797 | Recurring fees, overages, and credits |
| `Payments.csv` | `payments` | 242 | Successful and failed payment attempts |

The history covers January-October 2026 in USD; the fixed workshop reporting date is **November 3, 2026**. The seven tables intentionally resemble an operational billing system rather than a star schema.

## Before you start

The steps below apply to **Workshop with file upload**. For **Workshop with mirroring**, use its [source-readiness and access prerequisites](docs/workshop-mirroring.md#prerequisites) instead.

1. Download this repository from GitHub using **Code > Download ZIP**, extract it, and locate its `data` folder. You need only the seven `.csv` files.
2. Obtain access to a Fabric workspace on an eligible capacity and permission to create Lakehouse, semantic model, and Data Agent items. For the Data Agent and MCP exercises, Microsoft documents **paid F2+ or qualifying P1+ capacity** and applicable tenant AI settings.
3. Follow the [workshop guide](docs/workshop.md). No SQL database, mirroring, Python, notebooks, SQL commands, or custom pipeline are required for the main lab.

This repository provides sample data and instructions; it doesn't create Fabric resources or configure an MCP client for you. UI names and service prerequisites can change.
