# Build the semantic model

This lab models the seven Lakehouse tables directly. It deliberately keeps the operational-style data instead of creating a star schema. For production, consider a dimensional model, shared calendar, contract history, explicit measures, security, and stronger currency typing.

## Create and inspect

1. After all seven CSVs are loaded as tables, open the Lakehouse and select **New Power BI semantic model** on its ribbon (the label can appear as **New semantic model**).
2. Name it `Dealership Billing`, choose the workshop workspace, select all seven lowercase tables, and confirm. Fabric creates a Direct Lake semantic model.
3. Open **Open data model** if the model editor doesn't open automatically. Default semantic models aren't automatically created for new Lakehouses.
4. Inspect column types. Keys on both sides of each relationship must have matching types, dates must be dates, and amounts must be numeric. See [type checks](dataset.md#types-to-check-after-loading).
5. In model properties, set IDs to **Don't summarize**, format monetary columns as USD with two decimal places, and add descriptions. These settings don't change source data or its precision.

If the Lakehouse table schema is wrong, don't assume formatting converts text or fixes Delta types. Stop and use the no-code Dataflow Gen2 alternative in [troubleshooting](workshop.md#troubleshooting), then create or update the model from the correctly typed tables. Avoid silently creating a report that returns wrong totals.

## Relationships

CSV tables don't come with relationships. Remove automatically suggested relationships that don't match the list, then create these six **active, one-to-many, single-direction** relationships. The left side is the one side and filters the right side.

| One side | Many side |
|---|---|
| `dealerships[DealershipID]` | `subscriptions[DealershipID]` |
| `products[ProductID]` | `subscriptions[ProductID]` |
| `subscriptions[SubscriptionID]` | `usagerecords[SubscriptionID]` |
| `subscriptions[SubscriptionID]` | `invoicelines[SubscriptionID]` |
| `invoices[InvoiceID]` | `invoicelines[InvoiceID]` |
| `invoices[InvoiceID]` | `payments[InvoiceID]` |

Example: in model view, drag `dealerships[DealershipID]` onto `subscriptions[DealershipID]`, verify cardinality **one-to-many**, cross-filter direction **single**, and **active**, and save. Repeat for the other five pairs.

**Do not add an active `dealerships` to `invoices` relationship** in this simple model: it creates competing dealership-to-invoice-line filter paths. The source files share `DealershipID` but there is intentionally no active model relationship for it. In this model, a dealer filter travels to subscriptions, usage, and invoice lines, **not back to invoice headers or payments**. Product filters likewise can't allocate invoice-level balances/payments to products. There are no prebuilt measures that bridge this gap.

Consequently, dealer-level payment and overdue questions require the Data Agent to generate a correct virtual relationship/filtered calculation. Review the generated query and answer; it may fail or repeat totals. Don't present invoice-header or payment totals in a dealer-filtered report visual as reliable unless a suitable calculation/model redesign has been independently validated. For a production solution, add a properly designed semantic model and explicit measures.

## Make the model understandable

Keep the table and column names used in the workshop. Add concise table descriptions from [the dictionary](dataset.md), and descriptions for:

- `subscriptions[EndDate]`: inclusive end date; blank means open-ended.
- `subscriptions[MonthlyRate]`: negotiated recurring rate, not billed revenue.
- `usagerecords[Quantity]`: total usage before allowance.
- `invoicelines[LineAmount]`: signed billed charge or credit.
- `invoices[TotalAmount]`: invoice header total, not a line amount.
- `payments[Amount]`: attempted amount; only `Succeeded` is collected.

Hide technical key columns from ordinary report views if desired, but include their dependencies in the model's AI schema. Hiding fields is not a security control.

## Check the data without code

Create a simple report from the model:

1. Add a table visual with `invoicelines[ServiceMonth]` and the sum of `invoicelines[LineAmount]`. Filter to October 1, 2026. Expect **$66,728.00**.
2. Add `products[ProductName]` to break out October billing; **Carfax Reports (demo)** should be **$33,996.00**.
3. Filter `invoicelines[LineType]` to `Credit` and `ServiceMonth` to September 1, 2026. The signed sum should be **-$300.00**.
4. Remove filters between checks. If dates or amounts aren't usable, stop and correct their types before proceeding.

These are simple visual aggregations, not saved explicit measures. The Data Agent can attempt more complicated calculations, but natural-language generation isn't guaranteed. Use the [answer key](demo-scenarios.md), inspect query/evidence when available, and flag incorrect results rather than assuming success.
