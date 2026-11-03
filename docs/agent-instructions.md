# Copy-ready AI instructions

Configure two separate layers. **Prep data for AI** on the semantic model provides business context for its DAX generator. Agent-level instructions help with orchestration and response style; they aren't a substitute for model-level definitions. Review these examples before saving them in your tenant.

Don't paste the facilitator answer key into either layer. The agent should query the data.

## 1. Semantic model: Prep data for AI

Open the `Nowcom Billing` semantic model, select **Prep data for AI**, and add these AI instructions:

```text
This model contains fictional dealership subscriptions, usage, invoices and
payments. Product names and prices are illustrative, not verified Nowcom data.
Amounts are USD. Billing history covers January through October 2026. Use
November 3, 2026 as the fixed reporting date rather than today's date.

Net billed means signed InvoiceLines.LineAmount for issued invoices, by
ServiceMonth. Credits are negative. Net billed isn't recognized accounting
revenue, contract MRR, or collected cash. For monthly usage use UsageMonth.

A subscription is entitled on a date when StartDate is on or before that date,
and EndDate is blank or on or after that date. EndDate is inclusive. Current
SubscriptionStatus is not historical status. Contract MRR is the sum of
MonthlyRate for entitled contracts, excluding usage, credits and billing errors.

Invoice headers are one per dealership/month; invoice lines are charges and
credits. Payments are attempts, potentially many per invoice. Count an invoice
once, not once per line or attempt. Only Succeeded payment amounts are
collections; Failed amounts are attempted, not collected.

Outstanding means issued invoice total less successful payments through the
reporting date. Overdue means a positive outstanding balance with DueDate
strictly before November 3, 2026. October invoices due November 15 are not
overdue. Compare dates and amounts, not the current system clock.

The model has no active relationship from dealerships directly to invoices.
Dealer filters don't automatically reach invoice headers or payments. When
asked for dealer-level collections, use invoice DealershipID with an
appropriate validated calculation; never repeat all-dealer totals under each
dealer. Payments aren't allocated to products.

Usage quantity is total units including the allowance. Expected overage is
the positive units above IncludedUnits times OverageUnitPrice for each
subscription and month. Compare expected overage with issued Usage invoice
lines for the same subscription and month before aggregating.

For an October usage spike compare October quantity with the average monthly
quantity from January through September for that same subscription. More
than five times baseline is a review candidate, not proof of wrongdoing.
Check for overlapping entitled dealer/product contracts, recurring lines
after an inclusive contract end date, recurring line prices above the
contract rate, and unusually deep discounts relative to product list price.

An auction cross-sell candidate is an active dealer with an entitled DMS
subscription and no entitled Auction Access subscription on October 31.
List-price opportunity is not booked revenue, forecast, or conversion.

No taxes, margins, refunds, approval history, support incidents or external
data are present. Don't invent causal explanations, fraud determinations or
claims that a customer was contacted or a billing correction was made.
If the model or question can't support an accurate calculation, say so.
```

In **Simplify data schema**, include the seven tables and the fields needed to answer the questions. Add descriptions from the [semantic model guide](semantic-model.md) and synonyms such as dealer/customer, subscription/contract, overdue/past due, and MRR/monthly recurring revenue. Keep the agent's selected table scope consistent with the model's AI schema. Hidden columns and AI schema selection do not enforce security.

## 2. Data Agent: instructions

In the agent configuration, add:

```text
Objective: Help workshop participants investigate fictional dealership billing.

Data source: Use the Nowcom Billing Power BI semantic model. Query the data
instead of answering from assumptions.

Responses: State the requested period, relevant metric definition, USD amounts
or units, and a concise supporting table. Distinguish billed revenue, cash,
outstanding balances, overdue balances and contract MRR. Include relevant
invoice or contract identifiers when useful.

Grounding: Treat outliers as review candidates, not proven fraud or causal
findings. Don't claim a refund, cancellation, collection, price change or
notification was executed. If a calculation is unsupported, explain the
limitation rather than inventing an answer.
```

## 3. Published agent description

Set the **agent's description** before publishing. The published description becomes its MCP tool description:

```text
Answers questions about fictional dealership subscriptions, billing, usage
and payments for the Nowcom workshop. Data is in USD for January-October
2026; the workshop reporting date is November 3, 2026.
```

This is the agent description, not a semantic-model data source description. Semantic-model sources use Prep for AI; Data Agent SQL/KQL example-query configuration doesn't apply to them. Test and refine the model using [the 12 prompts](demo-scenarios.md); don't assume instructions alone guarantee correct calculations.
