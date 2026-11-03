# Twelve Data Agent demo scenarios and facilitator answer key

**Baseline:** original seed, all issued invoices, USD, reporting date November 3, 2026. October invoices aren't overdue yet. Contract snapshots use October 31 unless explicitly stated. All names/prices are fictional. Don't put this answer key into agent instructions.

Ask the quoted question, compare the response with the matching SQL result, and inspect its query/evidence when available. Formatting can vary; dealer/product sets and metrics must match. Full machine-readable rows are in [expected_results.json](../data/expected_results.json).

## 1. Understand recurring vs usage billing

> For October 2026, show net billed revenue by product, split into recurring fees, usage overages, and credits. Use USD and service month, not payment dates.

**Expected:** total **$66,728** = $30,655 recurring + $36,073 usage + $0 credits. Product totals: Carfax demo $33,996; DMS $11,677; CRM $7,176; Auction Access $6,499; Website $4,776; AutoCheck demo $1,924; Book Values $680.

**Business discussion:** consumption can change the billing mix independently of contract MRR. This is billed revenue, not recognized accounting revenue or collected cash.

**Model:** Net Billed, Recurring Billed, Usage Billed, Service Credits. **Reference:** [01_october_billing.sql](../sql/scenarios/01_october_billing.sql).

## 2. Prioritize overdue collections

> As of November 3, 2026, which dealerships have overdue invoice balances after successful payments? Show the overdue invoice count and balance per dealership, largest balance first.

**Expected:** Desert Mesa Motors **$3,765 / 2 invoices**; Coastal Bend Auto **$2,469.75 / 1**; Blue Canyon Auto **$985 / 1**. Total **$7,219.75**.

**Business discussion:** Blue Canyon has a partial payment; Coastal Bend's failed retries don't settle anything. October invoices are outstanding for some dealers but due November 15, so don't include them as overdue.

**Model:** Overdue Balance, invoice-level successful payment logic. **Reference:** [02_overdue_receivables.sql](../sql/scenarios/02_overdue_receivables.sql).

## 3. Find overlapping CRM contracts

> On October 31, 2026, which dealership/product pairs have more than one entitled subscription? Show the contract count, combined monthly recurring rate, and possible excess monthly rate assuming one contract is intended.

**Expected:** **Maple Grove Auto / Dealer CRM**, contracts `704` and `754`, **2 contracts**, combined **$598 MRR**, suspected excess **$299/month**. The second started September 1.

**Business discussion:** confirm entitlement/account structure before removing a contract. There is deliberately no uniqueness constraint on dealer/product.

**Model:** Duplicate Contract Count, October Contract MRR; inspect contract rows for rate exposure. **Reference:** [03_duplicate_subscriptions.sql](../sql/scenarios/03_duplicate_subscriptions.sql).

## 4. Detect billing after cancellation

> Which recurring services were billed for a service month after the subscription's inclusive end date? Show the dealership, product, end date, charge count, and total amount.

**Expected:** **Pinecrest Auto / Dealer Website**, end **August 31, 2026**, two charges for September and October, **$398 total**. Contract `1201`. The normally cancelled CRM contract at Clearwater is **not** a false positive.

**Business discussion:** review the billing scheduler and consider a customer correction; this isn't a payment refund already processed.

**Model:** Post Cancellation Billed. **Reference:** [04_post_cancellation_billing.sql](../sql/scenarios/04_post_cancellation_billing.sql).

## 5. Surface extreme vehicle-history usage

> Which subscriptions had October 2026 usage more than five times their January-September monthly average? Show dealer, product, October quantity, baseline average, multiple, and expected overage charge.

**Expected:** two **Carfax Reports (demo)** contracts. **Sunset Valley Motors:** 2,400 reports vs 80.22 average, **29.92x**, **$23,500** expected overage. **Willow Brook Motors:** 500 vs 77.78, **6.43x**, **$4,500** expected overage.

**Business discussion:** a spike can be legitimate usage, meter duplication, or another issue. The dataset doesn't prove the cause. Both must appear; omitting Willow Brook misses an independently large spike.

**Model:** October Usage Baseline Multiple with one subscription in context; Expected Overage filtered to October. **Reference:** [05_usage_spike.sql](../sql/scenarios/05_usage_spike.sql).

## 6. Review a deep negotiated discount

> Which contracts entitled on October 31, 2026 are at least 50 percent below the product's monthly list price? Show the dealership, product, list price, negotiated fee, monthly gap, and discount percentage.

**Expected:** **Summit Trail Motors / DMS**, list **$499**, contract **$199**, gap **$300/month**, **60.12% discount**. Contract `605`.

**Business discussion:** this may be an approved commercial concession, not an error. There's no approval workflow or cost/margin data in the dataset.

**Model:** Deep Discount Monthly Gap plus contract/catalog fields. **Reference:** [06_deep_discount.sql](../sql/scenarios/06_deep_discount.sql).

## 7. Catch a billed-rate overcharge

> In October 2026, which recurring invoice lines had a billed unit price above the negotiated contract monthly rate? Show the invoice, dealer, product, both rates, and overcharge.

**Expected:** **Oak Hollow Motors / DMS**, invoice **INV-202610-011**, billed **$999** vs contract **$499**, **$500 overcharge**.

**Business discussion:** the customer is overbilled even though the invoice header reconciles perfectly. Structural quality checks alone won't catch this.

**Model:** Rate Overcharge with October service-month filter. **Reference:** [07_rate_overcharge.sql](../sql/scenarios/07_rate_overcharge.sql).

## 8. Find unbilled overage revenue

> For October 2026, compare expected usage overage to issued usage charges per subscription. Which dealerships have a positive unbilled amount, and how much?

**Expected:** **Willow Brook Motors / Carfax demo**, **500 total reports**, **50 included**, **$10/report**, expected **$4,500**, usage charges **$0**, gap **$4,500**. Contract `1507`. Its $149 base fee is billed; don't call the entire subscription unbilled.

**Business discussion:** investigate the settlement-to-invoice process before issuing any corrective bill.

**Model:** Expected Overage and Unbilled Overage with UsageMonth October. **Reference:** [08_unbilled_usage.sql](../sql/scenarios/08_unbilled_usage.sql).

## 9. Separate failed attempts from invoices

> As of November 3, 2026, show dealerships with failed payment attempts, the number of failed attempts, distinct affected invoices, and the remaining outstanding balance of those invoices after successful payments.

**Expected:** **Coastal Bend Auto**, **6 failed attempts**, **2 invoices**, outstanding **$5,015.25**. Only September's $2,469.75 is overdue; October's $2,545.50 isn't due yet.

**Business discussion:** don't sum retry amounts as revenue loss or count each retry as an unpaid invoice. The failure code is InsufficientFunds, not a basis to infer intent or creditworthiness.

**Model:** Failed Payment Attempts; evaluate affected invoice IDs once and use Outstanding Balance for that invoice set. **Reference:** [09_failed_payment_attempts.sql](../sql/scenarios/09_failed_payment_attempts.sql).

## 10. Explain the contract run-rate change

> Compare entitled subscription counts and contract MRR on September 30 and October 31, 2026. Which ended subscription accounts for the change? Exclude usage, credits, and billed-rate errors.

**Expected:** September **125 / $30,455**; October **124 / $29,956**; change **-1 / -$499**. **Stonebridge Motors / DMS**, contract `2005`, ended September 30 with current status Suspended, explains the entire change.

**Business discussion:** this is a suspended product contract, **not a lost dealership account**. Snapshot queries use dates rather than today's status.

**Model:** September Contract MRR, October Contract MRR, Contract MRR Change, October Entitled Subscriptions; inspect ended contract rows for attribution. **Reference:** [10_contract_mrr_change.sql](../sql/scenarios/10_contract_mrr_change.sql) gives snapshot totals; drill into `SubscriptionID = 2005` for the attribution.

## 11. Account for a service credit

> Show September 2026 service credits by dealership, product, and reason code, using signed billed amounts.

**Expected:** **Golden Plains Auto / DMS / ServiceCredit**, **-$300**. One signed invoice credit, not a cash refund.

**Business discussion:** the credit reduces net billed revenue. No support ticket or incident record exists to establish its operational cause.

**Model:** Service Credits filtered to September. **Reference:** [11_service_credits.sql](../sql/scenarios/11_service_credits.sql).

## 12. Identify an auction cross-sell segment

> On October 31, 2026, which active dealership accounts have an entitled DMS subscription but no entitled Auction Access subscription? List the dealerships and regions, count them, and estimate the monthly list-price opportunity, not a sales forecast.

**Expected:** **13 dealerships**, at **$149/month** each = **$1,937/month** illustrative list opportunity. Names: Aspen Ridge, Cedar Ridge, Cypress Lane, Juniper Hill, Lakefront, Maple Grove, Meadow Park, Northstar, Oak Hollow, Prairie View, Silver Creek, Sunset Valley, and Willow Brook (full labels and regions are in the reference output).

**Business discussion:** eligibility is observable, conversion and demand aren't. Stonebridge must be excluded because its DMS is suspended. Northstar is deliberately an even-numbered dealer without auctions; don't infer ownership from dealer IDs.

**Model:** Auction Cross Sell Dealers, Auction Cross Sell List Opportunity. **Reference:** [12_cross_sell.sql](../sql/scenarios/12_cross_sell.sql).

## Evaluation and live-change caveat

Evaluate **all 12** against the clean baseline before the optional live payment. Correct results require dates, signs, units, charge types, invoice grain, and successful-payment filters. Record failures instead of accepting a plausible narrative.

After `sql\04_live_payment.sql`, Desert Mesa's overdue balance changes to **$1,920** and total overdue becomes **$5,374.75**. Baseline collection answers and payment counts no longer match. Revenue, contracts, usage, credit, and cross-sell fixtures remain unchanged.
