# Workshop with mirroring

This is the mirroring edition of [Workshop with file upload](workshop.md). It retains the seven-table semantic model, AI instructions, 12 business questions, and MCP exercises, but replaces CSV upload and **Load to tables** with **Fabric Mirroring from an existing Azure SQL Database**.

## What you'll build

**Azure SQL Database -> Fabric mirrored database / OneLake Delta tables -> Power BI semantic model -> Fabric Data Agent -> MCP client.**

| Source setting | Value |
|---|---|
| Connector | **Azure SQL Database**, not SQL Server or Azure SQL Managed Instance |
| Server | `kirbysqlserver2.database.windows.net` |
| Database | `dealership` |
| Suggested Fabric mirrored item name | `DealershipBillingMirrored` |

No separate Lakehouse, CSV download/upload, or table-loading pipeline is required. Mirroring performs an initial copy and then continuously replicates supported source changes into OneLake. **Zero-ETL ingestion means no custom ingestion ETL pipeline; it doesn't mean zero latency, no source configuration, or no semantic modeling.**

The server is the supplied workshop server; the source database name above follows the Dealership naming convention. Updating this guide does **not** rename an existing Azure SQL database. Before running the lab, the DBA must confirm that `dealership` exists on this server and contains the approved sample data. Connectivity, schema, contents, permissions, service tier, and mirroring readiness have **not** been verified by this repository. This guide doesn't provision or modify Azure/Fabric resources.

## Agenda (3 hours)

| Time | Topic | Outcome |
|---|---|---|
| 00:00-00:15 | Introduction to Fabric and mirroring | Understand OneLake, managed replication, semantic meaning, and Data Agents |
| 00:15-00:30 | Open/create the approved workspace and review source readiness | Confirm capacity, identity, network, permissions, and source eligibility |
| 00:30-01:05 | Configure Azure SQL Database mirroring | Select the seven tables and verify initial replication and SQL endpoint availability |
| 01:05-01:35 | Create a semantic model | Define six relationships and verify report results |
| 01:35-02:00 | Create and configure a Data Agent | Add the model, apply AI instructions, and publish |
| 02:00-02:35 | Explore 12 business questions | Compare responses with the facilitator answer key |
| 02:35-02:55 | Connect the Data Agent as an MCP server | Discover and call the published agent from an MCP client |
| 02:55-03:00 | Wrap-up | Discuss replication, permissions, and next steps |

Provisioning, security/network changes, and source preparation must be completed **before** the session. Initial replication time varies; don't promise completion within a fixed number of minutes.

## Prerequisites

### Fabric and participant access

- Sign in to [Microsoft Fabric](https://app.fabric.microsoft.com/) with a work/school account in the **same Microsoft Entra tenant as the Azure SQL source**. Cross-tenant Azure SQL Database mirroring isn't supported.
- Use an active capacity-backed workspace. For Data Agent and MCP, use **paid F2+ Fabric capacity** or **P1+ Premium capacity with Fabric enabled**, applicable AI/cross-geo tenant settings, regional availability, and appropriate Power BI licensing.
- The person creating Azure SQL mirroring in the Fabric portal needs workspace **Member or Admin**, not only Contributor: creation grants the Azure SQL server managed identity read/write access to the mirrored item and requires Reshare permission. Participants also need model authoring and necessary agent/data permissions.
- Have the Fabric administrator review the mirroring tenant settings documented by Microsoft: **Service principals can call Fabric public APIs** and **Users can access data stored in OneLake with apps external to Fabric**. Don't change tenant settings without approval.
- For MCP, use an approved client supporting streamable HTTP and Fabric authentication. Responses may leave Fabric's compliance boundary through the client.

### Source readiness: facilitator/DBA checklist

The existing database is the source; **don't create a new database or reseed `dealership` as a participant exercise**.

1. Confirm `dealership` is the writable primary and has a supported service tier. Microsoft's current guidance supports vCore tiers; DTU Free/Basic and Standard below 100 DTUs aren't supported. Check the [current eligibility guidance](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database#tier-and-purchasing-model-support).
2. Confirm no incompatible CDC, Azure Synapse Link, delayed transaction durability, or existing mirroring arrangement blocks setup. Review [Azure SQL mirroring limitations](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database-limitations) for table features and types as well.
3. In the Azure portal, open logical server `kirbysqlserver2` > **Security > Identity**. The DBA must verify an enabled primary managed identity; a **system-assigned identity** is the straightforward lab choice. User-assigned identity support has separate requirements and is documented as preview. Enabling/changing identity is an administrator action, not assumed permission from this guide.
4. Arrange an approved source login and mapped database user. The connection principal needs **SELECT**, **ALTER ANY EXTERNAL MIRROR**, **VIEW DATABASE PERFORMANCE STATE**, and **VIEW DATABASE SECURITY STATE** in `dealership`. The DBA should follow the [official tutorial's login/user setup](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database-tutorial#database-principal-for-fabric). Don't use or distribute a server administrator password as a workshop shortcut.
5. Confirm the approved Fabric-to-SQL network path. Use the organization's allowed public connectivity or a configured **virtual network/on-premises data gateway** with access to the SQL server, including private endpoint/firewall configuration where applicable. Don't open broad firewall access just for the lab.
6. If OneLake inbound access is restricted, the workspace admin must configure the Azure SQL server's Azure resource ID in **Resource Instance Rules** as documented in the tutorial.
7. Verify the seven tables and columns match the [shared data dictionary](dataset.md#tables-and-grain), with the fictional January-October 2026 baseline if using the answer key. Confirm supported types, keys, and monetary precision; unsupported columns can be omitted from replication, and some unsupported types/features can block a table entirely.
8. Configure downstream Fabric/model security before sharing: source SQL row-level permissions, object permissions, dynamic masking, and sensitivity labels **don't automatically carry over** to mirrored data.

**Shared-source workshop constraint:** an Azure SQL database can't be mirrored into another Fabric workspace if it's already mirrored elsewhere. Use **one approved shared mirror of `dealership`**, with the facilitator configuring it once; participants can build separate models/agents with unique names in the approved workspace. If a valid mirror already exists, use it and start at step 5. Don't stop an existing mirror or create competing copies for each attendee.

Capacity, source database, gateways, storage, and downstream query operations may incur charges. Use only approved fictional workshop data and follow organizational policies.

## 1. Introduction to Fabric

| Component | Role |
|---|---|
| Azure SQL Database | Existing operational source on `kirbysqlserver2.database.windows.net`, database `dealership` |
| Fabric mirrored database | Manages replication of selected tables into OneLake |
| OneLake | Stores the replicated Delta data without a custom ingestion ETL pipeline |
| SQL analytics endpoint | Read-only analytical query surface over the replicated tables |
| Semantic model | Adds relationships, business definitions, and Prep for AI context |
| Data Agent | Queries the authorized semantic model using natural language |
| MCP | Exposes the published agent as a discoverable tool to a compatible client |

The mirrored destination isn't the source Azure SQL database and isn't a separate Fabric SQL database (OLTP) item. Source writes happen in Azure SQL; the analytics copy is read-only. Replication and downstream model freshness have separate checkpoints.

## 2. Open or create the approved workspace

1. Ask the facilitator whether the shared `dealership` mirror already exists, and use that workspace when it does.
2. For the first setup only, select **Workspaces > New workspace**, name it `Dealership Mirroring Workshop` (or an approved unique name), and choose the eligible capacity. If needed, use **Workspace settings > Workspace type** to select the approved capacity.
3. Confirm Member/Admin access for the mirror creator and appropriate permissions for model/agent authors.
4. Confirm the source-readiness checklist above with the DBA and Fabric admin before proceeding.

**Checkpoint:** one approved target workspace, active capacity, and an eligible source. Don't change an existing workshop's permissions or mirroring state without approval.

## 3. Create the Azure SQL mirrored database item

The facilitator performs this once for the shared source. If already configured, open the existing item instead.

1. In the approved workspace, select **New item / Create** and search for **Mirrored Azure SQL Database**.
2. Create the item with display name `DealershipBillingMirrored` if the UI requests an item name. The **source database connection name remains `dealership`**, regardless of the Fabric display name.
3. Select **Azure SQL Database** as the source, then an approved existing connection or **New connection**.
4. Enter the following settings:

   | Connection field | Enter/select |
   |---|---|
   | Server | `kirbysqlserver2.database.windows.net` |
   | Database | `dealership` |
   | Connection name | An approved recognizable name, such as `DealershipAzureSQL` |
   | Data gateway | **None** only when direct connectivity is approved and works; otherwise the configured gateway |
   | Authentication kind | The DBA-provisioned supported method, such as Organizational account or Basic (SQL authentication) |

5. Sign in with the approved identity or enter the issued credentials in Fabric's connection dialog. Other supported methods, such as workspace identity/service principal, require their own administrator preparation. **Never place passwords, secrets, or tokens in this repository or participant instructions.**
6. Select **Connect**. If discovery fails, stop and resolve the reported identity/network/permissions issue with the administrator; don't bypass security controls.

## 4. Select tables and start replication

1. On **Configure mirroring**, turn **Mirror all data** **off**. Select only the seven workshop tables below, using their actual source schema and spelling.
2. The table names below are expected from the original dataset, **not a live inventory**. `dbo` is a common schema but hasn't been verified here. If required tables or columns differ, ask the facilitator to resolve the mismatch rather than substituting unrelated data.

   | Expected source table | Baseline rows, if unchanged |
   |---|---:|
   | `Dealerships` | 24 |
   | `Products` | 7 |
   | `Subscriptions` | 127 |
   | `UsageRecords` | 540 |
   | `Invoices` | 240 |
   | `InvoiceLines` | 1,797 |
   | `Payments` | 242 |

3. Review the selected objects, then select **Mirror database**. This starts the initial copy and ongoing replication.
4. Select **Monitor replication**. Wait for the initial copy to finish for **all seven tables**; confirm a healthy **Running** state and populated refresh information. Inspect per-table errors and excluded/unsupported columns, not just the item-level status.
5. Refresh the monitor while waiting. A partial set of healthy tables isn't sufficient to proceed to modeling.

**Checkpoint:** all seven selected tables have completed initial replication. This replaces all CSV upload and Load-to-tables actions from the file-upload edition.

## 5. Validate mirrored data and open the SQL analytics endpoint

1. Open the mirrored item and switch to its **SQL analytics endpoint** using the item/ribbon selector. Allow time for endpoint metadata to synchronize after the initial copy.
2. In the object explorer, confirm all seven tables and required columns are present under the actual schemas. Use table previews to inspect key, date, and amount values.
3. Compare row counts with the source as checked by the facilitator. The baseline counts above apply only if `dealership` contains the unchanged sample. Previews may be truncated; use report count aggregations after model creation for complete counts.
4. Verify required keys have compatible types, monetary fields are numeric, and date fields are usable. Source SQL types are mirrored rather than guessed from CSV, but unsupported types/columns still require review.
5. If counts or values differ, distinguish replication lag, missing schema/columns, and actual source changes. Don't overwrite the source or change the answer key to hide a failure.

The SQL endpoint is available for read-only analytical exploration and visual queries. No T-SQL scripts are required for this guide. A separate Lakehouse is not needed to make these tables usable by Power BI.

## 6. Create a semantic model

1. In the mirrored database's **SQL analytics endpoint**, select **New semantic model** (sometimes **New Power BI semantic model**).
2. Name it `Dealership Billing Mirroring` (add a participant suffix if needed), select the approved workspace and **only the seven mirrored workshop tables**, then confirm.
3. Open **Open data model** if the editor doesn't appear automatically. This flow creates a **Direct Lake** model; don't connect a new import model directly to Azure SQL by mistake.
4. Keep source schema/table mappings intact. For consistency with the shared instructions, rename the **semantic model table display names only** to `dealerships`, `products`, `subscriptions`, `usagerecords`, `invoices`, `invoicelines`, and `payments`. Don't rename source SQL objects or mirrored tables.
5. Remove conflicting auto-detected relationships. Add exactly these six **active, one-to-many, single-direction** relationships; the left side filters the right:

   | One side | Many side |
   |---|---|
   | `dealerships[DealershipID]` | `subscriptions[DealershipID]` |
   | `products[ProductID]` | `subscriptions[ProductID]` |
   | `subscriptions[SubscriptionID]` | `usagerecords[SubscriptionID]` |
   | `subscriptions[SubscriptionID]` | `invoicelines[SubscriptionID]` |
   | `invoices[InvoiceID]` | `invoicelines[InvoiceID]` |
   | `invoices[InvoiceID]` | `payments[InvoiceID]` |

6. Don't add an active `dealerships` -> `invoices` relationship: it creates competing dealership-to-invoice-line filter paths. Dealer filters in this model reach subscriptions, usage, and invoice lines, **not invoice headers or payments**. There are no prebuilt measures bridging that gap. Dealer-level collections questions remain stretch cases requiring correct generated calculations and independent validation.
7. Set IDs to **Don't summarize**, format monetary fields as USD with two decimals, and add descriptions. Reuse the [shared model descriptions and report checks](semantic-model.md#make-the-model-understandable), but **skip that guide's Lakehouse/CSV creation steps**.
8. Create a report with `invoicelines[ServiceMonth]` and Sum of `LineAmount`; filter to October 1, 2026. For the unchanged baseline, expect **$66,728.00**, with **$33,996.00** for Carfax demo and **-$300.00** September credits. Check all table counts with Count of each table's key, without filters.
9. In the model's **Prep data for AI**, apply the [shared semantic model AI instructions](agent-instructions.md#1-semantic-model-prep-data-for-ai). Where the guide names `Dealership Billing`, use your **`Dealership Billing Mirroring`** model. Include the required fields in the AI schema and save/apply the configuration.

**Checkpoint:** seven model tables, six unambiguous relationships, correct baseline checks (or a documented changed source baseline), and Prep for AI configured. Mirroring replicates data; it doesn't create business definitions or guarantee correct agent calculations.

## 7. Create and publish the Data Agent

1. Select **New item > Fabric data agent** and name it `Dealership Mirroring Analyst` (with a participant suffix if needed).
2. Add **your `Dealership Billing Mirroring` Power BI semantic model** as the only source, not the mirrored database itself. Select the seven tables.
3. Paste the [shared Data Agent instructions](agent-instructions.md#2-data-agent-instructions), replacing the model name in the instruction text with your actual model name. Apply business rules to the model's Prep for AI as well; agent instructions alone don't provide its DAX-generation definitions.
4. Ask: “What is October 2026 net billed revenue in USD?” For the unchanged baseline, expect **$66,728.00**. Inspect evidence/query when available.
5. Add the [published agent description](agent-instructions.md#3-published-agent-description), confirming that the described dates/data still match the approved source.
6. **Publish** for MCP and approved consumers. Verify agent/model/data permissions; source SQL access controls aren't automatically replicated security.

## 8. Try the 12 questions

Use the same [12 copy-ready prompts and facilitator answer key](demo-scenarios.md) as Workshop with file upload. This preserves billing/product mix, overdue balances, overlapping contracts, post-cancellation billing, usage spikes, deep discounts, overcharges, unbilled usage, failed payments, MRR changes, credits, and cross-sell.

The key assumes the original January-October 2026 fictional dataset and the fixed reporting date **November 3, 2026**, even when the real current date is later. If the Azure SQL data has changed, have the facilitator establish expected answers independently; don't claim the old key still matches.

Review values, units, signs, date filters, and customer/product sets. Questions involving dealer-level payments/collections are still **stretch cases** for the six-relationship model. Don't paste the answer key into AI instructions.

## 9. Call the agent as an MCP server

1. Open the **published `Dealership Mirroring Analyst`** > **Settings > Model Context Protocol** and copy **its** MCP URL.
2. Follow the [shared MCP client steps](mcp.md#1-copy-your-agents-mcp-details), substituting your mirroring agent/model names for `Dealership Billing Analyst` / `Dealership Billing`.
3. Add that HTTP MCP server in VS Code, authenticate with an authorized Fabric identity, discover the agent's tool, and ask the October billing question.
4. Compare the MCP answer with the agent chat and report visual for the same source state. The original **$66,728.00** checkpoint applies only to the unchanged baseline.
5. For a Python client, use the [same optional Python example](workshop.md#optional-call-the-mcp-server-from-python). Copy the **mirroring agent's** MCP URL into `MCP_URL`; no ingestion Python is needed. This link is only for the client example, not instructions to upload files.

The URL is a **Data Agent MCP endpoint**, not the SQL connection string or an arbitrary REST endpoint. The client must perform MCP initialization/discovery and send a valid Fabric token. See the [shared authentication and troubleshooting notes](mcp.md#authentication-and-limitations).

## Freshness and optional change demonstration

This workshop doesn't require writes to `dealership`. If a DBA separately approves a change demonstration, only that authorized person should make a controlled change to the dedicated demo source. Don't ask every participant to modify the shared database.

Observe the table in **Monitor replication**, then its SQL endpoint, then confirm the semantic model has reframed/refreshed to the current Delta state, and requery the report/agent. A running mirror doesn't prove the model is current; it also doesn't refresh an already displayed report or old chat response automatically. Don't stop/start mirroring as a refresh shortcut: stopping disables replication and starting reseeds tables.

## Troubleshooting

| Issue | What to check |
|---|---|
| Can't create mirrored item or grant identity access | Mirror creator must be workspace Member/Admin with required Reshare capability; have the admin verify tenant settings and permissions. |
| Source already mirrored elsewhere | Use the approved existing mirror/workspace. Don't disable another workshop's mirror to create your own. |
| Connection/authentication fails | Confirm the exact server/database, approved auth method, login/user mapping, four source permissions, network path, and same-tenant requirement. |
| Firewall/private network blocks access | Use the approved gateway/private connectivity path with the DBA/admin; don't weaken network policy. |
| Replication won't start or remains failed | Review primary managed identity, mirrored-item write permission, OneLake Resource Instance Rules if applicable, source tier, unsupported features/types, and per-table errors. |
| Missing columns or tables | Verify explicit table selection and type eligibility. Some columns can't mirror; some features/types block the table. Don't model incomplete data. |
| SQL endpoint doesn't show tables yet | Wait for initial replication and endpoint metadata synchronization; compare status before assuming zero rows. |
| Report/agent answer differs from answer key | Check source baseline, replication state, endpoint visibility, model freshness, types, relationships, and question date. Don't assume replication is instantaneous. |
| Dealer balances repeat across dealers | The simple model doesn't filter invoice headers/payments from dealerships. Review the documented stretch-case limitation and generated query. |
| MCP doesn't work | Publish first; use this agent's MCP URL, supported client authentication, and authorized agent/model identity. |

## References

- [Azure SQL Database mirroring overview and supported tiers](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database)
- [Configure Azure SQL Database mirroring: identity, permissions, network, and UI](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database-tutorial)
- [Azure SQL Database mirroring limitations](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database-limitations)
- [Monitor mirrored database replication](https://learn.microsoft.com/en-us/fabric/mirroring/monitor)
- [Create a Direct Lake semantic model from a SQL analytics endpoint](https://learn.microsoft.com/en-us/fabric/data-warehouse/create-semantic-model)
- [Shared AI instructions](agent-instructions.md)
- [Shared 12 questions and answer key](demo-scenarios.md)
- [Shared MCP guide](mcp.md)

Reviewed against Microsoft documentation on November 4, 2026. UI names and service requirements may change. No live source connection, mirroring setup, model, or agent has been tested by adding this guide.
