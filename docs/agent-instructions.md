# AI setup: keep model semantics separate from orchestration

The Data Agent's DAX generator uses **semantic-model metadata and Prep for AI**. It doesn't use agent-level instructions as a substitute for model calculation definitions. Configure both layers below. These are suggested workshop text for human review, not automatically deployed AI settings.

Don't paste the facilitator's answer key or expected result amounts into either layer. The agent must query the data.

## 1. Semantic model: Prep data for AI instructions

Open the `Nowcom Billing` semantic model, select **Prep data for AI**, and review/apply this text through the supported UI:

```text
This model contains fictional dealership subscription billing, not real Nowcom
customers or verified Nowcom prices. USD only. Baseline billing covers January
through October 2026. Use November 3, 2026 as the fixed reporting date; never
substitute today's date. Latest complete service month is October 2026.

Use explicit model measures. "Revenue" means Net Billed, signed issued invoice
lines by ServiceMonth, not GAAP recognized revenue or cash. Recurring Billed
is different from contract MRR. Service Credits are negative billed lines.
Use ServiceMonth or Invoices.BillingMonth for billed revenue. Use
UsageRecords.UsageMonth for meter reporting. PaymentDate is for cash timing.

Entitlement on a date means StartDate <= date and EndDate blank or >= date;
EndDate is inclusive. SubscriptionStatus is current, not historical status.
Use October Contract MRR and September Contract MRR for snapshots. Contract
MRR excludes usage, credits, and billed-price errors. It includes all entitled
contracts, even overlap candidates. A suspended product isn't a lost customer.

Invoices are dealer/month headers. InvoiceLines are charge/credit rows.
Payments are attempts, potentially many per invoice. Never sum invoice totals
after joining lines or individual attempts. Successful payments alone settle
an invoice. Failed attempts don't count as cash; distinguish attempt count,
distinct invoices, and distinct dealerships.

Use Outstanding Balance and Overdue Balance for invoice-level settlement.
Overdue means DueDate strictly before November 3, 2026, after subtracting
successful payments through that date. October invoices due November 15 aren't
overdue. Invoice-level cash/AR isn't allocated to products and returns blank
under direct product, subscription, or invoice-line filters.

The semantic model intentionally omits the physical Dealerships-to-Invoices
relationship to avoid ambiguous line filters. Cash/AR/failed-attempt measures
transfer dealership filters using TREATAS. Don't bypass these measures by
summing raw invoice or attempted-payment amounts.

Usage Quantity is total metered units, including the allowance. Expected
Overage = max(0, quantity - contract included units) * contract overage price.
Unbilled Overage compares that amount with issued Usage lines for the same
subscription and service month; compare before aggregating. A recurring base
fee doesn't settle a missing usage charge.

For usage outliers use October Usage Baseline Multiple with one subscription
in context; it divides October quantity by the January-September monthly
average. "Extreme" means more than five times that average.

Duplicate Contract Count means excess entitled contracts per dealer/product
on October 31. Suspected excess monthly rate assumes one contract was intended;
it isn't proof of an invalid contract. Deep discounts mean at least 50 percent
below list on entitled October contracts. Contracts and catalog terms aren't
historically versioned; rates are constant within each seeded contract.

Post Cancellation Billed means recurring lines with ServiceMonth after the
inclusive EndDate. Rate Overcharge compares recurring unit prices with the
negotiated contract rate, not the catalog list price. Cross-sell means active
dealers with entitled DMS but no Auction Access on October 31. List-price
opportunity isn't pipeline, conversion prediction, or booked revenue.

There are no taxes, costs, refunds, support tickets, VINs, approval histories,
contract amendments, or external market data. Don't invent causal explanations,
margins, incident details, discount approvals, or fraud determinations.
```

Also configure descriptions and measure formats from [semantic-model.md](semantic-model.md). Add synonyms such as Dealerships = dealers/customers; Subscriptions = contracts; Net Billed = billed revenue; Overdue Balance = past due receivables; Contract MRR = monthly recurring revenue; UsageRecords = meter settlements.

In **Simplify data schema**, include the seven tables and the fields/measures needed for these questions, plus their dependencies. Keep the same table scope in the Data Agent. If a necessary dependency is hidden for reports, ensure the AI configuration doesn't accidentally exclude it. Schema selection and hidden flags aren't security enforcement.

## 2. Data Agent: source description

```text
Nowcom Billing is a semantic model over seven mirrored fictional dealership
billing tables. It supports billed revenue, collections, contract run rates,
meter-to-bill comparisons, subscription review, and auction cross-sell.
Business definitions and the fixed reporting date live in its measures,
metadata, and Prep for AI configuration.
```

## 3. Data Agent: orchestration and response instructions

```text
Objective: Help workshop participants investigate fictional dealership billing.

Data source: Use only the Nowcom Billing Power BI semantic model attached to
this agent. Retrieve results rather than answering from assumptions.

Responses: Give the requested period, metric definition, USD amounts or units,
and a concise supporting table. Distinguish billed revenue, cash, outstanding
balances, overdue balances, and contract run rate. Show supporting invoice or
contract identifiers when useful and available.

Grounding: Describe data-quality or business-rule outliers as review candidates,
not proven fraud or causal findings. Don't claim a refund, cancellation,
collection, price change, or customer notification was executed. This agent
only analyzes data. If a requested concept isn't represented, say so.

Freshness: For live-change demonstrations, confirm the requested reporting
date and acknowledge that replication/model visibility can lag source commits.
```

These guide orchestration/response style; keep computational rules in the model. For model sources, don't treat SQL/KQL few-shot query inputs as DAX-generation examples. Optional **Verified answers** should be reviewed/configured in Prep for AI using real report/model outputs, not hardcoded expected numbers. First validate questions 1, 2, 8, 10, and 12; then evaluate the full twelve-question script.
