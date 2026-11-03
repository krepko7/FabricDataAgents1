# Semantic model and reporting lab

## Preserve the seven-table source

Create `Nowcom Billing` as a **Direct Lake** semantic model over all seven mirrored base tables. The source remains OLTP; there is no star-schema conversion, materialized reporting layer, extra date table, or data-copy pipeline.

This intentionally trades some model simplicity for source fidelity. Production analytics often benefits from a dimensional model, a proper calendar, historical contract changes, and more extensive security. Here, use explicit dates and snapshot measures rather than classic calendar-based time intelligence.

From the mirrored item's **SQL analytics endpoint**, choose **New semantic model**, select the seven tables, and save to the workshop workspace. Open **Open data model** to edit it. Default semantic models are no longer created automatically; don't assume one already exists.

## Relationships: configure explicitly

Remove any auto-detected relationships first. Use exactly these **six active, single-direction, one-to-many** relationships, filtering from left to right:

| One side | Many side |
|---|---|
| `Dealerships[DealershipID]` | `Subscriptions[DealershipID]` |
| `Products[ProductID]` | `Subscriptions[ProductID]` |
| `Subscriptions[SubscriptionID]` | `UsageRecords[SubscriptionID]` |
| `Subscriptions[SubscriptionID]` | `InvoiceLines[SubscriptionID]` |
| `Invoices[InvoiceID]` | `InvoiceLines[InvoiceID]` |
| `Invoices[InvoiceID]` | `Payments[InvoiceID]` |

**Do not add an active Dealerships -> Invoices relationship.** It would introduce two dealership-to-line paths (through contracts and through invoice headers). The physical SQL foreign key still exists; not every physical foreign key needs a semantic-model relationship.

The supplied cash/AR/failed-attempt measures use `TREATAS` to transfer dealership filters to invoice headers. That virtual relationship is for calculation only; **it is not a security boundary or an RLS implementation**. Product/subscription/line filters deliberately return BLANK for invoice-level cash and AR measures. Payments aren't allocated to products, and showing a whole invoice balance on every product would be misleading.

No bidirectional relationships and no inactive relationships are needed. Don't enable automatic relationship detection again after setup.

## Metadata

For copy/paste consistency, retain the supplied technical table/column names during the lab; measure names are business-friendly. This is a deliberate demo compromise. Add descriptions and user-facing synonyms in **Prep data for AI**; a production model can rename fields after updating all DAX references.

Set integer keys to Whole number, date fields to Date, `RecordedAt` to Date/time, amounts/rates to Fixed decimal number with USD currency formatting, and `Quantity`/`IncludedUnits` to Whole number. Hide relationship IDs from the report field list, and set IDs/terms to **Don't summarize**. Keep business identifiers such as InvoiceNumber and ContractReference available for drill-through.

Hide base aggregate columns such as `LineAmount`, `Amount`, and `TotalAmount` from report authors after creating explicit measures. These aren't access controls: include dependencies in the model's AI schema when necessary for calculations. Leave dates available and use them directly; disable auto date/time if working through Desktop.

Copy the table grains from [the dictionary](dataset.md) into table descriptions. Add short column descriptions for the important ambiguities:

| Object | Suggested description |
|---|---|
| `Subscriptions[EndDate]` | Last entitled date, inclusive; blank means open-ended. Use dates, not current status, for historical snapshots. |
| `Subscriptions[MonthlyRate]` | Negotiated recurring monthly fee in USD; not catalog price and not actual billed revenue. |
| `UsageRecords[Quantity]` | Total monthly usage before allowance. Never confuse with billed excess quantity on invoice lines. |
| `InvoiceLines[ServiceMonth]` | First day of billed service month. Use to filter billed revenue. |
| `Invoices[BillingMonth]` | Invoice's service month, not payment month. Invoice header grain is dealership/month. |
| `Invoices[TotalAmount]` | Stored header total; never sum after joining to lines or individual payment attempts. |
| `Payments[Amount]` | Attempted USD amount. Include only Succeeded for cash or settlement. |
| `Payments[PaymentDate]` | Payment attempt date. Cash is recognized here for demo collection reporting. |
| `Products[MonthlyListPrice]` | Illustrative catalog list price, not a contract rate or forecast. |

## Add and persist measures

Open [measures.dax](../semantic-model/measures.dax). It is a runnable **DAX query with query-scoped definitions**, not an automatically deployed model.

1. Paste the file in DAX query view and run it against the completed relationships.
2. Resolve any errors before continuing. Cloud source bindings and DAX execution must be checked in your own model.
3. Use **New measure** in each specified host table, copying `Measure Name = expression` from its `MEASURE 'HostTable'[Measure Name] = expression` definition. Don't include `DEFINE`, `MEASURE`, or the final `EVALUATE` in a New measure formula.
4. Persist all definitions, not just the six output measures. Where DAX query view offers **Update model with changes**, you can instead review and apply the definitions there.
5. Apply the formats/descriptions below, save, reopen the model, and verify the measures remain present. A query-scoped test alone doesn't persist them.

| Measures | Format and meaning |
|---|---|
| Demo As Of Date | `yyyy-mm-dd`; fixed 2026-11-03, not system date |
| Net Billed, Recurring Billed, Usage Billed, Service Credits | `$#,##0.00`; signed issued line amounts, filter by service month |
| Collected Cash | `$#,##0.00`; successful payments through fixed reporting date; dealer/invoice grain only |
| Outstanding Balance, Overdue Balance | `$#,##0.00`; one balance per invoice; overdue means due strictly before reporting date |
| October Contract MRR, September Contract MRR, Contract MRR Change | `$#,##0.00`; date-specific recurring run rate; no usage or billed-price errors |
| October Entitled Subscriptions, Duplicate Contract Count | `#,##0`; duplicates count excess contracts per dealer/product, not necessarily duplicate bills |
| Deep Discount Monthly Gap | `$#,##0.00`; active contracts at least 50% below catalog; gap isn't proven leakage |
| Post Cancellation Billed, Rate Overcharge | `$#,##0.00`; signed recurring billing after end, or positive price excess over contract |
| Expected Overage, Unbilled Overage | `$#,##0.00`; calculated per usage settlement before aggregation |
| October Usage Baseline Multiple | `0.00"x"`; October quantity / Jan-Sep average, only when exactly one subscription is selected |
| Failed Payment Attempts | `#,##0`; failed processor rows, not distinct invoices or customers |
| Auction Cross Sell Dealers | `#,##0`; active DMS accounts without Auction Access on October 31 |
| Auction Cross Sell List Opportunity | `$#,##0.00`; eligible dealer count times auction list fee; not a forecast |

Add these meanings as measure descriptions and group measures in display folders such as Billing, Collections, Contracts, Usage, and Review Candidates. Source terms don't change historically in this demo, so comparing a past line to today's stored contract rate is valid **only within this dataset's scope**.

### Sanity checks with no report filters

The final ROW in `measures.dax` should return:

| Check | Expected |
|---|---:|
| October Net Billed | $66,728.00 |
| Overdue Balance | $7,219.75 |
| October Contract MRR | $29,956.00 |
| MRR Change (October minus September) | -$499.00 |
| October Unbilled Overage | $4,500.00 |
| Auction Cross Sell Dealers | 13 |

Test a matrix by DealershipName using Overdue Balance: Desert Mesa $3,765; Coastal Bend $2,469.75; Blue Canyon $985. Filter Products to DMS and verify AR becomes BLANK rather than repeating invoice balances. Clear that product filter for cash/collections pages.

Also test the known split-payment account: Prairie View Cars' October invoice must have zero outstanding, with two successful attempts. Failed payment attempts must total six for Coastal Bend Auto, while distinct affected invoices are two.

## Suggested report pages

| Page | Visuals | Correct filter choices |
|---|---|---|
| Billing overview | Net/recurring/usage cards, monthly billed line chart, product bar chart | `Invoices[BillingMonth]` or `InvoiceLines[ServiceMonth]` for billing; Dealerships region/name |
| Collections | Overdue/outstanding/cash cards, dealer balance matrix, invoice drill-through | Dealer filters and invoice dates; **no product/subscription/line slicer** |
| Subscription review | October MRR, MRR change, duplicate count, cancellation billing and discount matrices | Snapshot measures are fixed to named dates, not driven by an invoice-month slicer |
| Usage and growth | Expected/unbilled overage by dealer/product, baseline multiple, auction opportunity | `UsageRecords[UsageMonth]` for usage; baseline measure already fixes Oct vs Jan-Sep |

Do not sync a billing-month slicer to usage or contract calculations and assume it filters those tables. There is no shared date dimension, and single-direction relationships don't propagate from invoices back to contracts or usage. Label pages/slicers accordingly.

For the cross-sell page, filter rows to `[Auction Cross Sell Dealers] > 0`. For the usage outlier page, put Dealer and Product on rows, select Carfax, and filter `[October Usage Baseline Multiple] > 5`. For duplicate review, filter `[Duplicate Contract Count] > 0`.

## Prep for AI and freshness

Apply the **model-level** guidance in [agent-instructions.md](agent-instructions.md) through **Prep data for AI**. Include all seven tables and required dependencies, align the agent's selection, and add synonyms such as dealer/customer, subscription/contract, overdue/past due, and MRR/monthly recurring revenue. Hiding fields or choosing an AI schema isn't RLS or OLS.

A Direct Lake model is not a guarantee of zero-latency answers. After replication catches up, refresh/reframe the semantic model as appropriate for its configuration, refresh report visuals, and start a fresh agent conversation before comparing a live update. SQL views over the endpoint can force a different storage/query path; use the mirrored **base tables** for this lab.
