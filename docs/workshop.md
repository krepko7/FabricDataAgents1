# Workshop: Zero ETL to data insights with Fabric Data Agents

## Outcomes and audience

Audience: Nowcom business stakeholders, billing/finance analysts, application engineers, and Fabric/Power BI practitioners. Work in pairs with a dedicated demo database and workspace per team, or use one instructor-managed environment with read-only participants.

By the end, participants can explain Fabric and OneLake, configure Azure SQL mirroring, model transactional tables without a star-schema rewrite, query the SQL analytics endpoint through T-SQL and a visual editor, and evaluate a Data Agent against 12 reproducible business scenarios.

This is a fictional billing demo, not an assessment of Nowcom's actual systems. The agent retrieves and aggregates governed data; it doesn't prove fraud, infer causes from external events, change subscriptions, or initiate collections.

## Three-hour agenda

Source provisioning/loading and access checks are **prework**, not part of the three-hour session. Budget 20-30 minutes for them, plus organizational approval lead time.

| Time | Duration | Topic | Hands-on outcome |
|---|---:|---|---|
| 00:00-00:15 | 15 min | Introduction to Fabric | Explain OneLake, mirroring, SQL analytics, semantic models, and Data Agents |
| 00:15-00:50 | 35 min | Set up and use SQL Mirroring for zero ETL | Seven Azure SQL tables replicated and initial counts reconciled |
| 00:50-01:25 | 35 min | Create a semantic model on the mirrored tables | Six unambiguous relationships and saved explicit measures |
| 01:25-01:50 | 25 min | Query the SQL analytics endpoint with T-SQL and Visual query | Equivalent October billing results with both query experiences |
| 01:50-02:15 | 25 min | Create a Fabric Data Agent on the semantic model | Model-level AI context configured; agent connected to the semantic model |
| 02:15-02:50 | 35 min | Test the Fabric Data Agent with 12 demo questions | Compare generated results with the answer key and identify limitations |
| 02:50-03:00 | 10 min | Discuss findings and close | Review business actions, security, cost, and production next steps |

For slower-paced delivery, extend to four hours rather than skipping relationship and answer validation.

## Prework checklist

| Owner | Required preparation |
|---|---|
| Azure owner | Create a dedicated, writable primary Azure SQL Database. Use vCore purchasing or DTU Standard S3/100 DTUs or higher. DTU Free/Basic and Standard below 100 DTUs aren't mirroring-compatible. Don't provision a Fabric SQL database instead. |
| Azure owner | Enable the Azure SQL logical server's **system-assigned managed identity** and make it the primary identity. User-assigned identity is an alternative currently in preview; system-assigned is the simpler workshop path. |
| Network owner | Approve a supported source connection. Prefer organization-approved private connectivity/gateway where required. Don't broadly expose a database or enable "Allow Azure services" without approval. Use the current mirroring networking guidance. |
| Fabric admin | Provide an active workspace capacity. The complete Data Agent lab requires **paid F2+ or qualifying P1+ capacity** and Fabric enabled; a mirroring-only trial doesn't establish Data Agent eligibility. Verify region availability. |
| Fabric admin | Review required tenant settings: service principals can call Fabric public APIs; users can access OneLake data with external apps; Data Agent AI/cross-geo processing and storing settings as applicable to the tenant/region. Enable only approved scopes. |
| Workspace owner | Give the person configuring mirroring **Member or Admin**, not only Contributor. For model/report authors, provide the appropriate write/Build permissions and Power BI licensing. The agent-only consumer path can use semantic-model Read access. |
| Facilitator | Clone/open this repository; load schema/seed into Azure SQL; run source validation; keep the answer key available but don't paste it into the agent's instructions. |
| Participants | Sign in to Azure/Fabric, verify source connectivity and workspace access, and arrange Power BI Pro or other appropriate report authoring/sharing licensing. No separate Azure OpenAI key is required. |

If OneLake inbound access is restricted, a workspace admin must also configure the logical SQL server's Azure resource ID in the workspace Resource Instance Rules as described in Microsoft's tutorial.

### Prepare the source

From the repository root:

```powershell
.\scripts\Load-Demo.ps1 -Server '<server>.database.windows.net' -Database 'NowcomBillingDemo'
```

Or run `sql\01_schema.sql`, `sql\02_seed.sql`, and `sql\03_validate.sql` in that order in a query tool connected to Azure SQL.

**Checkpoint:** all seven counts match the README/manifest and validation returns PASS. The seed includes 24 fictional dealerships, seven products, 127 contracts, and 240 monthly invoices. Don't proceed with partial data.

### Prepare the mirroring connection principal

Use the approved authentication method: Microsoft Entra organizational account/workspace identity/service principal, or SQL authentication where permitted. Never commit passwords or client secrets. The following illustrates the current Entra login-and-mapped-user path; have an authorized administrator substitute an existing approved identity.

In the Azure SQL logical server's **master** database, connected as an authorized Entra administrator:

```sql
CREATE LOGIN [approved-identity@yourtenant.example] FROM EXTERNAL PROVIDER;
```

In the **NowcomBillingDemo user database**:

```sql
CREATE USER [approved-identity@yourtenant.example]
    FOR LOGIN [approved-identity@yourtenant.example];
GRANT SELECT, ALTER ANY EXTERNAL MIRROR,
      VIEW DATABASE PERFORMANCE STATE, VIEW DATABASE SECURITY STATE
TO [approved-identity@yourtenant.example];
```

Entra server logins are currently preview for Azure SQL; see the linked tutorial for the supported authentication options and limitations in your tenant. Don't grant db_owner to every participant as a shortcut. The identity establishing the source connection is distinct from the SQL server managed identity that publishes to OneLake.

Check that CDC, Synapse Link, and mirroring to a different Fabric workspace aren't enabled on the source database. This lab doesn't enable CDC or require you to enable change tracking.

## Lab 1 - Introduction to Fabric (15 minutes)

Explain the journey: **Azure SQL OLTP source -> Mirroring -> OneLake mirrored base tables -> SQL analytics endpoint / Direct Lake semantic model -> Reports / Fabric Data Agent**.

Discuss the roles:

| Component | Purpose in this demo |
|---|---|
| Azure SQL Database | Operational system of record; all writes happen here |
| Mirroring | Managed initial copy and continuous changes into OneLake without a custom ETL pipeline |
| OneLake | Shared analytical storage, with managed Delta tables |
| SQL analytics endpoint | Read-only T-SQL access to the mirrored data plus query/visual exploration |
| Power BI semantic model | Relationships, business metrics, descriptions, and governed analysis |
| Fabric Data Agent | Natural-language questions translated into queries against selected governed sources |

"Zero ETL" removes the custom extraction/loading pipeline here; it does **not** remove source preparation, business modeling, data-quality work, replication delay, or security design.

**Checkpoint:** ask participants which endpoint should receive a payment INSERT. Correct answer: Azure SQL, not the mirrored SQL analytics endpoint.

## Lab 2 - Set up and use SQL Mirroring (35 minutes)

1. In Fabric, open the dedicated capacity-backed workshop workspace.
2. Select **Create / New item**, search for **Mirrored Azure SQL Database**, and create `Nowcom Billing Mirror`.
3. Add an Azure SQL connection using the actual server FQDN and database name. Select the approved authentication and gateway configuration; connect using the principal prepared in prework.
4. In Configure mirroring, turn off **Mirror all data** and explicitly select the seven `dbo` base tables. This keeps future accidental tables out of the demo.
5. Select **Mirror database** and open **Monitor replication**. Wait for initial snapshots to finish; check each table, not just the item-level status. Initial copy usually takes minutes but isn't a fixed SLA.
6. Open the item's SQL analytics endpoint. Confirm all seven tables are visible. If SQL metadata isn't ready yet, wait and refresh; Running replication alone doesn't prove endpoint/model readiness.
7. Run the count query below and compare with `data\manifest.json`.

```sql
SELECT 'Dealerships' AS TableName, COUNT(*) AS [Rows] FROM dbo.Dealerships
UNION ALL SELECT 'Products', COUNT(*) FROM dbo.Products
UNION ALL SELECT 'Subscriptions', COUNT(*) FROM dbo.Subscriptions
UNION ALL SELECT 'UsageRecords', COUNT(*) FROM dbo.UsageRecords
UNION ALL SELECT 'Invoices', COUNT(*) FROM dbo.Invoices
UNION ALL SELECT 'InvoiceLines', COUNT(*) FROM dbo.InvoiceLines
UNION ALL SELECT 'Payments', COUNT(*) FROM dbo.Payments;
```

**Checkpoint:** counts are 24, 7, 127, 540, 240, 1,797, and 242 respectively. Preview pages may show only 1,000 records; use SQL counts.

Source RLS, object permissions, masking, and sensitivity labels are **not automatically inherited** by mirrored data. In this synthetic lab use only approved workspace access; production requires deliberate OneLake, endpoint, model, and agent security design.

## Lab 3 - Create a semantic model (35 minutes)

Follow [the semantic model guide](semantic-model.md):

1. In the SQL analytics endpoint, select **New semantic model**, include the seven mirrored base tables, and name it `Nowcom Billing`. Open the data model.
2. Remove automatically inferred relationships. Add exactly the six documented active single-direction relationships.
3. Set types, hide technical fields from reports, disable inappropriate numeric summarization, and describe grains/terms.
4. Run `semantic-model\measures.dax` in DAX query view. Persist all definitions with New measure or the reviewed Update model option. Set formats/descriptions and save.
5. Verify the six sanity-check outputs and the dealer-level AR matrix. Product-filtered AR should be blank, not duplicated.
6. If time permits, create the Billing overview and Collections report pages. Use the correct date fields and avoid product slicers on collections.

**Checkpoint:** no ambiguous relationship warning; October billed = $66,728; overdue = $7,219.75; October contract MRR = $29,956. Confirm measures persist after reopening.

Don't use invoice revenue as MRR or failed attempts as collected cash. These distinctions are the business value of the semantic layer.

## Lab 4 - T-SQL and Visual query (25 minutes)

### Part A: T-SQL

Open the **SQL analytics endpoint**, not the source database. Create a SQL query and paste/run:

1. `sql\scenarios\01_october_billing.sql`: signed October billing by product and charge type.
2. `sql\scenarios\02_overdue_receivables.sql`: overdue customer balances, aggregating successful payments **before** joining invoices.
3. `sql\scenarios\08_unbilled_usage.sql`: usage settlement vs billed overage, including missing invoice usage lines.

All 12 scenario files are SELECT-only and can run on the source or mirrored SQL endpoint. `sql\01_schema.sql`, `02_seed.sql`, `03_validate.sql`, and `04_live_payment.sql` are source-side scripts; don't run them at the read-only endpoint.

### Part B: Visual query

1. In the SQL analytics endpoint, create a **New visual query**.
2. Add `InvoiceLines`, then filter `ServiceMonth` to **2026-10-01**.
3. Merge with `Subscriptions` on `SubscriptionID`, using an inner join, and expand `ProductID`.
4. Merge that result with `Products` on `ProductID`, expanding `ProductName`.
5. Merge with `Invoices` on `InvoiceID`, expand `InvoiceStatus`, and filter to Issued.
6. Keep `ProductName` and `LineAmount`; group by `ProductName` with **Sum of LineAmount**, named `NetBilled`. Sort descending.
7. Run the query, inspect the generated SQL, and compare the seven product totals to scenario 01. Sum the displayed totals: $66,728.
8. Save as `October billing by product - visual`.

Use Power Query diagram/step controls as exposed in your tenant's editor; labels can evolve. Don't sum `Invoices.TotalAmount` in the line-grain query, and don't merge raw payment attempts into invoice lines.

**Checkpoint:** the visual result matches the NetBilled column of T-SQL scenario 01, including Carfax demo $33,996 and DMS $11,677.

## Lab 5 - Create a Data Agent on the semantic model (25 minutes)

1. Open `Nowcom Billing` and **Prep data for AI**. Review/apply the **model-level instructions** in [agent-instructions.md](agent-instructions.md), configure the AI schema with all necessary dependencies, and add the proposed synonyms. Save.
2. Create a **Fabric data agent** item in the same workspace named `Nowcom Billing Analyst`.
3. Add **only the `Nowcom Billing` Power BI semantic model** as the data source. Don't also add the mirrored database: that would allow routing around the semantic layer during this exercise.
4. Select the seven model tables consistently with Prep for AI. Confirm required fields/measures are available.
5. Add the separate **agent-level orchestration/response instructions** from the same file. Describe the data source as fictional dealership billing with fixed-date definitions.
6. Ask a simple question: "What is October 2026 net billed revenue in USD?" Inspect the returned evidence/query where available and expect $66,728.
7. Save/publish the agent for the workshop test audience using your tenant's supported sharing controls. Confirm each tester's actual data/model permissions; sharing an agent doesn't replace source authorization.

**Important:** semantic-model DAX generation relies on model metadata and Prep for AI. Agent-level instructions do **not** supply DAX-generation business rules. SQL/KQL example-query features are not a substitute for this setup; don't upload the T-SQL answer files as semantic-model DAX examples.

**Checkpoint:** one semantic-model source is attached and the agent can retrieve a correct baseline number, rather than reciting numbers embedded in instructions.

## Lab 6 - Test all 12 demo questions (35 minutes)

Use [the 12-question demo script](demo-scenarios.md). Start a fresh conversation for each question or explicitly restate dates and scope. Divide questions among teams to cover all 12 in the allotted time.

For each question, record the returned period, values, evidence/query if exposed, pass/fail, and any misleading claims. Compare against `data\expected_results.json` and the matching SQL file; then reproduce mismatches in a report or DAX query.

**Pass:** correct dealer/product set and numeric results (currency within $0.01, ratios within 0.01), correct metric/date interpretation, and no fabricated causal claims. A fluent narrative with the wrong number fails.

If the agent misses an answer, improve the measure/metadata/Prep for AI configuration and retry in a fresh conversation. Don't "fix" the prompt by feeding it the answer. Prebuilt measures and verified-answer configurations can improve consistency, but no untested model can guarantee every natural-language phrasing.

### Optional live zero-ETL moment

Do this **after** collecting all baseline results, because it intentionally changes them.

1. Record Desert Mesa Motors' overdue balance ($3,765) using scenario 02.
2. Connect to the **Azure SQL source** and run `sql\04_live_payment.sql` once. It pays the August invoice in full and returns the collected amount.
3. Watch the Payments replication status and query the mirrored endpoint until the new ProcessorReference `DEMO-LIVE-804` is visible. No ETL/pipeline job is run.
4. Re-run scenario 02: Desert Mesa now has one overdue invoice and a balance of **$1,920** (a $1,845 reduction).
5. Refresh/reframe the Direct Lake model as appropriate, refresh the report, and start a fresh agent conversation. Ask for the same dealer's overdue balance as of November 3.
6. Discuss replication, SQL endpoint metadata/data visibility, model framing, and conversational caching as distinct freshness boundaries.

The script refuses a duplicate run; it never creates another table or modifies the invoice amount. Original baseline answer keys no longer apply to collection questions after this step. Use a new demo database for a clean baseline rehearsal.

## Troubleshooting checkpoints

| Symptom | Check/action |
|---|---|
| Mirroring can't connect | Source server/database, tenant alignment, credentials, minimal permissions, server primary managed identity, approved networking/gateway |
| Tables don't replicate | Supported tier, no conflicting CDC/Synapse Link/other workspace mirror, per-table status, supported types; this schema avoids unsupported types |
| Row counts differ | Source validation first; wait for initial replication and SQL endpoint availability; compare actual counts rather than preview rows |
| Semantic model unavailable | Create it explicitly; default models aren't automatically generated |
| Billed totals multiply | Relationship ambiguity or joining header/payment totals to line-grain data; restore the six-edge model |
| Dealer AR is identical on every row | Missing TREATAS measures or an unintended relationship; use the supplied explicit AR measures |
| Product-filtered AR is blank | Expected: no payment allocation to products in this seven-table source |
| Agent unavailable | Paid-capacity eligibility, tenant AI/cross-geo policy, regional availability, user/item permissions |
| Agent ignores billing definitions | Put them in the semantic model's Prep for AI, not only agent instructions |
| Agent gives stale live-change results | Verify source commit, replication, endpoint result, model freshness, then fresh conversation in that order |

## Close and production discussion (10 minutes)

Have each team identify an owner/action for a collection issue, a revenue leakage candidate, and a customer-experience billing defect. Explain why a high usage multiple or discount is a **review candidate**, not causal proof.

Discuss production extensions: contract version history, taxes/refunds, unit-cost and margin data, allocation of cash to products, dimensional modeling/calendar, RLS/OLS and least privilege, service limits, monitoring, data-agent evaluation, and approved human-led remediation. None are silently claimed by this demo.

Resource owners should stop/remove only dedicated lab resources under their retention/cost policies. Never delete shared customer resources or disable shared security settings as workshop cleanup.

## Official references

Reviewed for this workshop on 2026-11-03; UI labels and preview capabilities can change.

- [Azure SQL mirroring overview and supported tiers](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database)
- [Azure SQL mirroring setup, identities, permissions, and networking](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database-tutorial)
- [Azure SQL mirroring limitations and security inheritance](https://learn.microsoft.com/en-us/fabric/mirroring/azure-sql-database-limitations)
- [Explore mirrored data and the SQL analytics endpoint](https://learn.microsoft.com/en-us/fabric/mirroring/explore)
- [Visual query editor](https://learn.microsoft.com/en-us/fabric/data-warehouse/visual-query-editor)
- [Create a Direct Lake semantic model](https://learn.microsoft.com/en-us/fabric/data-warehouse/create-semantic-model)
- [Create a Fabric Data Agent and prerequisites](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent)
- [Semantic model best practices for Data Agents](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)
- [Data Agent configurations](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations)
