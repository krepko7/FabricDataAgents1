# Workshop Express with file upload: 12 Data Agent questions

Use the **copy icon** on each text block to paste the question into the Data Agent. Expected answers below are for the provided Express CSV, not live customer data. All amounts are USD; the fixed reporting date is November 3, 2026.

These questions are adapted for the **single table**. They don't require invoice/payment data or model relationships. The anomaly flags and monetary differences are precomputed, so this lab demonstrates conversational exploration of prepared metrics, not autonomous anomaly detection.

## 1. October billing and product mix

```text
For October 2026, show net billed revenue by product in USD, split into RecurringBilled, UsageBilled, and Credits. Include the overall total. Use MonthStart for the period.
```

**Expected:** **$66,728.00** total = **$30,655.00** recurring + **$36,073.00** usage + **$0.00** credits.

| Product | Net billed |
|---|---:|
| Carfax Reports (demo) | $33,996.00 |
| Dealer Management System | $11,677.00 |
| Dealer CRM | $7,176.00 |
| Auction Access | $6,499.00 |
| Dealer Website | $4,776.00 |
| AutoCheck Reports (demo) | $1,924.00 |
| Vehicle Book Values | $680.00 |

**Check:** billed amounts aren't cash collected or recognized accounting revenue.

## 2. Top billed dealerships

```text
Which five dealerships have the highest NetBilled in October 2026? Show each dealership and its total in USD, largest first.
```

| Expected dealership | Net billed |
|---|---:|
| Sunset Valley Motors | $24,885.75 |
| Coastal Bend Auto | $2,545.50 |
| Pinecrest Auto | $2,495.00 |
| Oak Hollow Motors | $2,189.00 |
| Summit Trail Motors | $2,144.50 |

**Check:** a high billing total isn't proof of profitability or successful collection.

## 3. Overlapping contracts

```text
For October 2026, filter OverlapAtMonthEnd to 1. Show the dealership, product, subscription IDs, number of entitled contracts, and combined ContractMRR. Assuming one contract was intended, what is the possible excess monthly rate?
```

**Expected:** **Maple Grove Auto / Dealer CRM**, contracts **704** and **754**; **2** entitled contracts; combined **$598.00 MRR**; possible excess **$299.00/month**.

**Check:** two flagged contracts represent **one overlapping dealer/product pair**, not two duplicate pairs. Verify the commercial arrangement before acting.

## 4. Billing after cancellation

```text
Across January-October 2026, find rows with positive PostEndBilled. Show dealership, product, subscription ID, inclusive EndDate, service months, and total PostEndBilled.
```

**Expected:** **Pinecrest Auto / Dealer Website**, contract **1201**, ended **August 31, 2026**; September and October **$199.00 each**, **$398.00 total**.

**Check:** this identifies service-month billing after contract end; it doesn't demonstrate a refund.

## 5. Usage spikes

```text
For October 2026, filter UsageSpikeFlag to 1. Show dealership, product, subscription ID, UsageQuantity, UsageBaselineJanSep, UsageMultiple, and ExpectedOverage. Round the average and multiple to two decimals.
```

| Expected dealership / Carfax Reports (demo) | Contract | Quantity | Baseline | Multiple | Expected overage |
|---|---|---:|---:|---:|---:|
| Sunset Valley Motors | 907 | 2,400 | 80.22 | 29.92x | $23,500.00 |
| Willow Brook Motors | 1507 | 500 | 77.78 | 6.43x | $4,500.00 |

**Check:** the baseline is each subscription's fixed nine-month average; don't sum multiples or infer fraud.

## 6. Deep discounts

```text
For October 2026, filter DeepDiscountFlag to 1. Show dealership, product, subscription ID, MonthlyListPrice, MonthlyRate, DiscountGap, and DiscountPercent as a percentage.
```

**Expected:** **Summit Trail Motors / Dealer Management System**, contract **605**; list **$499.00**, negotiated **$199.00**, gap **$300.00/month**, discount **60.12%**.

**Check:** the stored discount is a fraction, not 60.12 dollars. Approval and margin data aren't present.

## 7. Recurring overcharge

```text
For October 2026, which subscription-month rows have positive RecurringOvercharge? Show dealership, product, subscription ID, MonthlyRate, RecurringBilled, and RecurringOvercharge.
```

**Expected:** **Oak Hollow Motors / Dealer Management System**, contract **1105**; rate **$499.00**, billed **$999.00**, overcharge **$500.00**.

**Check:** this metric is already prepared from the original recurring invoice lines; don't claim the agent corrected the bill.

## 8. Unbilled usage

```text
For October 2026, find positive UnbilledOverage. Show dealership, product, subscription ID, UsageQuantity, IncludedUnits, OverageUnitPrice, ExpectedOverage, UsageBilled, and UnbilledOverage.
```

**Expected:** **Willow Brook Motors / Carfax Reports (demo)**, contract **1507**; **500 reports**, **50 included**, **$10.00** per excess report; expected **$4,500.00**, usage billed **$0.00**, gap **$4,500.00**.

**Check:** its base fee was billed. An unbilled usage gap isn't an unpaid invoice balance.

## 9. Billed revenue versus contract MRR

```text
For October 2026, compare total NetBilled with total ContractMRR and calculate the difference. Break the difference into UsageBilled, Credits, and RecurringBilled minus ContractMRR. Do not describe the difference as cash collected.
```

**Expected:** net billed **$66,728.00** vs MRR **$29,956.00**; gap **$36,772.00** = **$36,073.00** usage + **$0.00** credits + **$699.00** recurring-minus-MRR. In this snapshot the last $699 is the $500 overcharge plus $199 post-end website billing.

**Check:** MRR is a month-end contract snapshot, not an invoice amount. These equalities describe this dataset, not a universal billing reconciliation rule.

## 10. Run-rate change

```text
Compare September 2026 and October 2026 separately: sum EntitledAtMonthEnd and ContractMRR for each month, then calculate October minus September. Which contract ended between the two month-end snapshots?
```

**Expected:** September **125 contracts / $30,455.00 MRR**; October **124 / $29,956.00**; change **-1 / -$499.00**. **Stonebridge Motors / Dealer Management System**, contract **2005**, ended **September 30, 2026**.

**Check:** EndDate is inclusive, so this contract is entitled on September 30 but not October 31. Don't sum both monthly snapshots.

## 11. Service credit

```text
For September 2026, show nonzero Credits by dealership, product, and CreditReason, preserving the sign. What is the total credit in USD?
```

**Expected:** **Golden Plains Auto / Dealer Management System / ServiceCredit**, **-$300.00**.

**Check:** a signed invoice credit isn't evidence of a cash refund.

## 12. Auction cross-sell

```text
For October 2026, filter DMSWithoutAuctionFlag to 1. List distinct dealership names and regions, count the dealerships, and calculate the illustrative Auction Access list-price opportunity at USD 149 per dealership per month. Do not use the DMS list price or call this a sales forecast.
```

**Expected:** **13 dealerships**, **$1,937.00/month** illustrative opportunity.

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

**Check:** Stonebridge is excluded because its DMS contract ended. List-price opportunity isn't booked revenue or a conversion prediction.

## Evaluation

A pass requires correct periods, customer/product sets, counts, units, and signed monetary values to the cent. Compare ratios and discounts to two decimal places. Inspect query/evidence where available. If a question fails, record the mismatch and review types, model selection, AI configuration, and aggregation grain; don't treat a fluent answer as proof.
