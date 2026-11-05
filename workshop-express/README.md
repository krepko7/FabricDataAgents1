# Workshop Express with file upload

**Two CSVs, two Lakehouse tables, one relationship, one Data Agent.** This shorter version of the Dealership workshop uses consolidated monthly subscription/billing data plus a small product lookup, so participants learn relationship building without loading all seven operational tables.

The data is **fictional**. Dealerships, prices, and product labels are illustrative, not verified Dealership offerings or customer information. AutoCheck/Carfax labels don't imply a vendor integration or endorsement.

## Agenda (60-75 minutes)

| Minutes | Activity                                                    |
| ------- | ----------------------------------------------------------- |
| 0-5     | Understand the dataset and business questions               |
| 5-15    | Create a Lakehouse, upload two CSVs, and load two tables    |
| 15-30   | Create a semantic model, relate products to billing, and configure Prep for AI |
| 30-40   | Create, instruct, and test the Data Agent                   |
| 40-60   | Try the 12 questions, dividing them among teams if needed   |
| 60-75   | Optional extra time to compare answers and discuss findings |

Capacity provisioning, tenant approvals, and sign-in should be completed beforehand. This resource does **not** include mirroring, pipelines, notebooks, ingestion scripts, or MCP setup. The [Workshop with file upload](../docs/workshop.md) remains available separately.

## Resources

| Resource                                                              | Purpose                                                                                                    |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [Workshop Express with file upload PowerPoint](Workshop-Express.pptx) | 20-slide facilitator deck with editable architecture graphic, lab steps, and question/answer speaker notes |
| [DealershipBilling.csv](data/DealershipBilling.csv)                   | Billing data: 1,262 rows and 32 columns, including `ProductID` instead of `ProductName`                     |
| [Products.csv](data/Products.csv)                                     | Product lookup: 7 rows, with `ProductID` and `ProductName`                                                 |
| [Data dictionary](dataset.md)                                         | Grain, types, precomputed metrics, and limitations                                                         |
| [Copy-ready AI instructions](ai-instructions.md)                      | Separate semantic model and Data Agent instructions                                                        |
| [12 copy-ready questions and answer key](demo-scenarios.md)           | Test the agent and check results                                                                           |

## Before the session

1. Download the repository: on [GitHub](https://github.com/krepko7/FabricDataAgents1), select the green **Code** button above the file list, then **Download ZIP**. Extract the ZIP and open `workshop-express`, then `data`. Use **both** `DealershipBilling.csv` and `Products.csv` from this folder, not the original seven CSVs in the repository's top-level `data` folder.
2. Sign in to [Microsoft Fabric](https://app.fabric.microsoft.com/) with an authorized work/school account.
3. Use a workspace on an active **Fabric capacity of F2 or higher (example: F4)**.
4. If you need a workspace, select **Workspaces > New workspace**, give it a unique name, and choose your approved capacity in the creation settings or **Workspace settings > Workspace type**. If unavailable, ask the administrator for an approved existing workspace. Capacity resources may incur charges.

## 1. Understand the two tables

Each row represents **one subscription in one month**, January-October 2026. A contract appears in multiple months; `SubscriptionID` alone isn't unique. `MonthStart` plus `SubscriptionID` is the row key.

Dealer labels are included in billing, but **product names live only in `products`**. Each product has one unique `ProductID`; many billing rows reference that same ID. All other billing columns and prepared metrics remain in `dealershipbilling`. Invoice lines are aggregated before consolidation, so billed amounts aren't repeated per invoice line. Invoice headers and payments are omitted: collections, outstanding balances, and overdue questions are outside Express scope.

Use USD and a fixed reporting date of **November 3, 2026**. Filter to a single month for contract MRR, entitled counts, discounts, overlap, and cross-sell questions; those snapshots must not be added across months.

## 2. Create a Lakehouse and load both CSVs

1. In your approved workspace, select **New item**, search for **Lakehouse**, and create `DealershipLH` (add a unique suffix if necessary).
2. In the Lakehouse explorer, select **...** next to **Files > Upload > Upload files**. Upload `DealershipBilling.csv` and `Products.csv` from the extracted `workshop-express\data` folder.
3. Select **...** next to `DealershipBilling.csv` > **Load to tables > New table**.
4. Keep the default schema if shown. Name the table **`dealershipbilling`** using lowercase letters.
5. Check **Column header**, set **Separator** to a comma, and select **Load**.
6. Repeat **Load to tables > New table** for `Products.csv`, naming the table **`products`**, with headers on and comma separator. Wait for both loads, expand **Tables**, and preview both tables.
7. Check the [expected column types](dataset.md#column-types-and-definitions): `ProductID` must be a **whole number in both tables**, amounts/ratios numeric, flags and counts whole numbers, and dates parsed correctly. Blank `EndDate` and non-October usage comparisons are null.

**Checkpoint:** `dealershipbilling` has **1,262 rows** and `products` has **7 unique, nonblank ProductIDs**. The preview may show only 1,000 billing rows; verify the full count in the report in step 7. Don't use **Append** to rerun either load, because it duplicates rows. Uploading a changed CSV does not automatically refresh its Delta table.

**Already completed the old one-table lab?** The billing file now has `ProductID` instead of `ProductName`. Reload it into a new table/model (use unique names if necessary), and load the lookup too. Don't append the new schema to the old table or assume re-uploading replaces it.

The loader infers types and doesn't offer a custom column schema. If dates or numeric fields load incorrectly, stop and use the [Workshop with file upload no-code type-correction guidance](../docs/workshop.md#troubleshooting), then use the corrected table. Formatting text as currency doesn't convert it into numbers. For production currency, use a governed fixed-precision ingestion process rather than relying on CSV inference.

## 3. Create the semantic model and Prep for AI

1. In the Lakehouse ribbon select **New Power BI semantic model** (sometimes **New semantic model**).
2. Name it `Dealership Billing SM`, select your workshop workspace, select **both `dealershipbilling` and `products`**, and confirm. This creates a Direct Lake semantic model.
3. Open its model editor in **Model view**. If editing is read-only, switch to **Editing** with the required model permissions. Confirm `ProductID` has the same whole-number type in both tables.
4. Drag **`products[ProductID]` onto `dealershipbilling[ProductID]`**, or use **Manage relationships > New relationship**. Configure the relationship below and save. If Fabric detected it automatically, inspect/edit that relationship instead of creating a duplicate.

   | Setting | Value |
   | --- | --- |
   | Lookup / one side | `products[ProductID]` |
   | Billing / many side | `dealershipbilling[ProductID]` |
   | Cardinality | **One to many (1:*)** from products to billing; if billing is shown first, **Many to one (*:1)** |
   | Cross-filter direction | **Single**, from `products` to `dealershipbilling` |
   | Active | **Yes** |

5. Confirm the model diagram shows **`products (1) -> (*) dealershipbilling`** with one active relationship. Use **`products[ProductName]`** for product labels, slicers, and grouping; the billing table no longer has a `ProductName` column. A product filter should filter billing amounts, not the other way around. Don't use a many-to-many or bidirectional relationship.
6. Select **Prep data for AI** in the model editor. In **AI instructions**, paste the [semantic model instructions](ai-instructions.md#semantic-model-prep-for-ai). Include **both tables**, both `ProductID` columns, `products[ProductName]`, and the required billing metrics in the AI schema. Save/apply.
7. OPTIONAL: Check the column types against the [dictionary](dataset.md). Set both `ProductID` columns, `SubscriptionID`, flags, contract rates, list prices, allowances, and ratios to **Don't summarize** by default.
8. OPTIONAL: Format the monetary fields as USD with two decimal places. Format `DiscountPercent` as **Percentage** with two decimal places, not currency: the stored value `0.60120240` means **60.12%**. Format `UsageMultiple` as a decimal, not a percent.

**Checkpoint:** two model tables and one active **1:\*** relationship. If product totals all repeat the grand total or a blank product appears, check the relationship, ID types, unique lookup IDs, and missing matches before proceeding. This quick lab uses precomputed numeric columns and simple aggregations, not a production semantic layer with explicit measures or a calendar. Agent-generated DAX still needs evaluation; instructions alone don't guarantee correct answers.

## 4. Create and configure the Data Agent

1. In the workspace select **New item**, search for **Fabric data agent**, and create `Dealership Analyst`.
2. Add the **`Dealership Billing SM` Power BI semantic model**, not the raw Lakehouse, as the only data source.
3. Select **both `dealershipbilling` and `products`** in the agent's table/schema selection.
4. Open the agent's instructions and paste the [Data Agent instructions](ai-instructions.md#data-agent-instructions). The semantic model's business rules belong in **Prep for AI**, not just here.
5. Ask: “What is October 2026 net billed revenue in USD?” Expect **$66,728.00**. Inspect the returned evidence/query if available.
6. Save the agent. **Publish** if participants will consume its published version; share only with approved participants who also have the necessary model/data permissions.

Semantic-model sources use Prep for AI for DAX-generation context. Agent-level SQL example-query and data source description settings aren't the configuration path for this source type. Don't paste the facilitator answer key into either instruction layer.

## 5. Test with 12 business questions

Open [the 12 questions](demo-scenarios.md). Each prompt has a copy-to-clipboard code block and an expected answer. Start fresh chats or restate the month for independent questions.

Check amounts, periods, signs, units, and customer/product sets. Outliers are **review candidates**, not proven fraud or causal findings. If the answer is wrong, first check column types, the chosen semantic model, Prep for AI, and the month filter; don't present a fluent response as correct without checking it.

**Completion:** participants have loaded two files to two tables, related products to billing in one semantic model, configured both instruction layers, and evaluated Data Agent responses. No cloud resources have been created by this repository, and these UI/model/agent steps haven't been exercised in a live workshop tenant.

## 6. Run ad-hoc SQL

1. Click your workspace on the left menu, then click the link for the DealershipLH of type "SQL Analytics Endpoint".
2. Pick "New SQL Query" from the menu and run the query (or similar) select top 10 \* from dealershipbilling.
3. Pick "New SQL Query" from the menu again and pick "New Visual Query".
4. Expand the tables on the left in the Explorer menu and drag the table dealershipbilling to the query canvas.
5. Click the blue + sign to the right of the table icon in the query canvas and pick "keep rows" and enter a number like 10.
6. You will see the results of your visual query below.

## 7. Auto-Create a report

1. Click back to your workspace menu on the far left menu.
2. Pick the 'Dealership Billing SM' semantic model.
3. Now click "New report" in the top right menu.
4. Add a table visual with **`products[ProductName]`** and **Sum of `dealershipbilling[NetBilled]`**. Filter `dealershipbilling[MonthStart]` to **October 1, 2026**. Each product must show its own amount, not the same grand total; compare the seven rows with [question 1](demo-scenarios.md#1-october-billing-and-product-mix). The overall total is **$66,728.00**, including **$33,996.00** for Carfax Reports (demo).
5. Add a slicer with **`products[ProductName]`** and select **Dealer Website**. Net billed must become **$4,776.00** for October. Clear the product slicer: **Sum of `ContractMRR`** must show **$29,956.00** and **Sum of `EntitledAtMonthEnd`** must show **124**. Remove the month filter and use **Count of `SubscriptionID`**, not distinct count, to check **1,262 billing rows**.

## References

- [Load CSV files to Lakehouse tables](https://learn.microsoft.com/en-us/fabric/data-engineering/load-to-tables)
- [Create a semantic model](https://learn.microsoft.com/en-us/fabric/data-warehouse/create-semantic-model)
- [Prep data for AI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-prepare-data-ai)
- [Create a Fabric Data Agent](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent)
- [Configure Data Agent data sources](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-add-datasources)

UI labels, prerequisites, and capabilities can change; confirm availability before the session.
