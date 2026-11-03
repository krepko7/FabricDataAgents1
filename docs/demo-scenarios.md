# Twelve Data Agent questions and facilitator answer key

These are evaluation prompts for the **clean CSV snapshot**, using USD and a fixed reporting date of **November 3, 2026**. The baseline covers January-October 2026. Ask the question, inspect the agent's evidence or generated query when available, and compare the result with the expected answer below.

The first questions are straightforward; multi-table comparisons and dealer-level collections are stretch cases. The no-code model has **no active dealership-to-invoice relationship and no prebuilt measures**, so the agent must construct correct calculations on its own. If it can't, don't present its answer as correct; document the result as an opportunity for further modeling. Instructions alone don't guarantee successful DAX generation.

## 1. Billed revenue and product mix

> For October 2026, show net billed revenue by product in USD, split into recurring fees, usage overages and credits. Use service month, not payment dates.

**Expected:** total **$66,728.00** = $30,655 recurring + $36,073 usage + $0 credits. Product totals: Carfax demo $33,996; DMS $11,677; CRM $7,176; Auction Access $6,499; Website $4,776; AutoCheck demo $1,924; Book Values $680.

**Discussion:** consumption changes billed revenue independently of contract MRR. This isn't recognized accounting revenue or collected cash.

## 2. Overdue collections

> As of November 3, 2026, which dealerships have overdue invoice balances after successful payments? Show the overdue invoice count and balance per dealership, largest balance first.

**Expected:** Desert Mesa Motors **$3,765 / 2 invoices**; Coastal Bend Auto **$2,469.75 / 1**; Blue Canyon Auto **$985 / 1**. Total **$7,219.75**.

**Discussion:** Blue Canyon has a partial payment; Coastal Bend's failed retries don't settle anything. October invoices aren't overdue yet. This is a dealer-to-invoice **stretch case** for the workshop model.

## 3. Overlapping CRM contracts

> On October 31, 2026, which dealership/product pairs have more than one entitled subscription? Show the contract count, combined monthly recurring rate, and possible excess monthly rate assuming one contract is intended.

**Expected:** **Maple Grove Auto / Dealer CRM**, contracts `704` and `754`, **2 contracts**, combined **$598 MRR**, suspected excess **$299/month**. The second started September 1.

**Discussion:** verify the business arrangement before assuming the second contract is invalid.

## 4. Billing after cancellation

> Which recurring services were billed for a service month after the subscription's inclusive end date? Show dealer, product, end date, charge count and total amount.

**Expected:** **Pinecrest Auto / Dealer Website**, end **August 31, 2026**, two charges for September and October, **$398 total**. Contract `1201`.

**Discussion:** investigate the billing process; the dataset doesn't show that a refund or correction occurred.

## 5. Usage spikes

> Which subscriptions had October 2026 usage more than five times their January-September monthly average? Show dealer, product, October quantity, baseline average, multiple and expected overage charge.

**Expected:** **Sunset Valley Motors / Carfax demo**: 2,400 reports vs 80.22 average, **29.92x**, **$23,500** expected overage. **Willow Brook Motors / Carfax demo**: 500 vs 77.78, **6.43x**, **$4,500** expected overage.

**Discussion:** both are review candidates, not proven meter errors. Compute each subscription's baseline before comparing.

## 6. Deep discount

> Which contracts entitled on October 31, 2026 are at least 50 percent below the product's monthly list price? Show dealer, product, list price, negotiated fee, monthly gap and discount percentage.

**Expected:** **Summit Trail Motors / DMS**, list **$499**, contract **$199**, gap **$300/month**, **60.12% discount**. Contract `605`.

**Discussion:** this may be an approved concession; approval and margin data aren't present.

## 7. Billed-rate overcharge

> In October 2026, which recurring invoice lines had a billed unit price above the negotiated contract monthly rate? Show invoice, dealer, product, rates and overcharge.

**Expected:** **Oak Hollow Motors / DMS**, invoice **INV-202610-011**, billed **$999** vs contract **$499**, **$500 overcharge**.

**Discussion:** an invoice can reconcile to its lines and still have the wrong rate.

## 8. Unbilled overage

> For October 2026, compare expected usage overage to issued usage charges per subscription. Which dealerships have a positive unbilled amount, and how much?

**Expected:** **Willow Brook Motors / Carfax demo**, **500 total reports**, **50 included**, **$10/report**, expected **$4,500**, usage charges **$0**, gap **$4,500**. Contract `1507`. Its $149 base fee was billed.

**Discussion:** compare usage and charges per subscription/month, not just grand totals.

## 9. Failed payment attempts

> As of November 3, 2026, show dealerships with failed payment attempts, the number of failed attempts, distinct affected invoices, and remaining outstanding balances of those invoices after successful payments.

**Expected:** **Coastal Bend Auto**, **6 failed attempts**, **2 invoices**, outstanding **$5,015.25**. Only September's $2,469.75 is overdue; October's $2,545.50 isn't due yet.

**Discussion:** retries aren't distinct invoices or collected cash. This is a dealer-to-invoice stretch case.

## 10. Contract run-rate change

> Compare entitled subscription counts and contract MRR on September 30 and October 31, 2026. Which ended subscription accounts for the change? Exclude usage, credits and billed-rate errors.

**Expected:** September **125 / $30,455**; October **124 / $29,956**; change **-1 / -$499**. **Stonebridge Motors / DMS**, contract `2005`, ended September 30 with current status Suspended.

**Discussion:** one suspended product doesn't mean the dealership account was lost.

## 11. Service credit

> Show September 2026 service credits by dealership, product and reason code, using signed billed amounts.

**Expected:** **Golden Plains Auto / DMS / ServiceCredit**, **-$300**.

**Discussion:** it's an invoice credit, not a recorded cash refund.

## 12. Auction cross-sell

> On October 31, 2026, which active dealership accounts have an entitled DMS subscription but no entitled Auction Access subscription? List the dealerships and regions, count them, and estimate the monthly list-price opportunity, not a sales forecast.

**Expected:** **13 dealerships**, at **$149/month** each = **$1,937/month** illustrative list opportunity. Full labels and regions:

| Dealership | Region |
|---|---|
| Aspen Ridge Motors | Midwest |
| Cedar Ridge Motors | West |
| Cypress Lane Cars | West |
| Juniper Hill Motors | Midwest |
| Lakefront Auto Mall | Midwest |
| Maple Grove Auto | West |
| Meadow Park Auto | South |
| Northstar Auto | Northeast |
| Oak Hollow Motors | Midwest |
| Prairie View Cars | South |
| Silver Creek Cars | West |
| Sunset Valley Motors | South |
| Willow Brook Motors | South |

**Discussion:** opportunity at list price isn't a conversion prediction. Stonebridge is excluded because its DMS subscription ended September 30.

## Evaluation

A useful response has the correct dealer/product set, time period, units, charge type, and values to the cent; usage ratios should match to 0.01. For complex cases, review generated query/evidence and calculate at the correct grain. A fluent response with incorrect numbers is not a pass. Discuss uncertain results and next modeling steps rather than presenting the agent as infallible.
