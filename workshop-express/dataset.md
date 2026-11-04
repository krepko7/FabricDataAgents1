# Workshop Express data dictionary

Use only [NowcomBillingExpress.csv](data/NowcomBillingExpress.csv). It is a comma-delimited UTF-8 file with headers, **1,262 rows and 32 columns**, derived from the full workshop's unchanged synthetic CSVs. No participant scripts are required.

**Grain:** one subscription/month, uniquely identified by `MonthStart` plus `SubscriptionID`. Rows begin in the subscription's start month and continue through October 2026, including ended contracts with zero month-end entitlement. Dealer and product labels are denormalized. Dates use `yyyy-MM-dd`; decimals use a period.

Issued invoice lines are aggregated to this grain **before** joining contract/product labels and monthly usage. There are no invoice header totals or payment amounts to duplicate. Monthly `RecurringBilled`, `UsageBilled`, `Credits`, and `NetBilled` reconcile to the original issued invoice lines for all ten months.

## Column types and definitions

| Column | Intended type | Meaning / aggregation |
|---|---|---|
| `MonthStart` | Date | Service month; filter October using `2026-10-01`, not the reporting date |
| `SubscriptionID` | Whole number, don't summarize | Contract identifier; repeated across months |
| `DealershipName` | Text | Fictional customer; unique dealership labels in this dataset |
| `Region` | Text | Dealer region |
| `ProductName` | Text | Illustrative service label |
| `StartDate` | Date | Contract start, inclusive |
| `EndDate` | Nullable date | Contract end, inclusive; blank means open-ended |
| `MonthlyListPrice` | Numeric USD, don't summarize | Product list fee, repeated per contract/month |
| `MonthlyRate` | Numeric USD, don't summarize | Negotiated recurring rate, even after the contract ends |
| `IncludedUnits` | Whole number, don't summarize | Monthly contract allowance; not total usage |
| `OverageUnitPrice` | Numeric USD, don't summarize | Charge per excess unit |
| `UsageUnit` | Text | Reports, auctions, lookups, or None |
| `EntitledAtMonthEnd` | Whole number 0/1 | Sum within **one month** for entitled subscription count, not dealership count |
| `ContractMRR` | Numeric USD | Negotiated rate if entitled at month end, otherwise zero; sum within **one month** |
| `RecurringBilled` | Numeric USD | Sum of issued Recurring lines for the subscription/month |
| `UsageBilled` | Numeric USD | Sum of issued Usage lines for the subscription/month |
| `Credits` | Numeric USD | Sum of issued Credit lines; negative |
| `NetBilled` | Numeric USD | RecurringBilled + UsageBilled + Credits; additive across service months |
| `UsageQuantity` | Whole number | Total usage including allowance; don't mix different usage units |
| `ExpectedOverage` | Numeric USD | max(0, UsageQuantity - IncludedUnits) * OverageUnitPrice |
| `UnbilledOverage` | Numeric USD | max(0, ExpectedOverage - UsageBilled), calculated per subscription/month |
| `RecurringOvercharge` | Numeric USD | Sum of positive (billed recurring unit price - MonthlyRate) * billed quantity |
| `PostEndBilled` | Numeric USD | Recurring charges whose service MonthStart is strictly after the inclusive EndDate |
| `OverlapAtMonthEnd` | Whole number 0/1 | This contract is entitled and the same dealer/product has multiple entitled contracts that month |
| `DiscountPercent` | Numeric fraction, don't summarize | (MonthlyListPrice - MonthlyRate) / MonthlyListPrice; e.g., 0.60120240 = 60.12% |
| `DiscountGap` | Numeric USD | Positive list-minus-contract rate if entitled at month end; otherwise zero |
| `DeepDiscountFlag` | Whole number 0/1 | Entitled at month end and discount at least 50% |
| `UsageBaselineJanSep` | Nullable numeric, don't summarize | Only populated for October usage contracts with positive baseline: Jan-Sep total / 9 calendar months |
| `UsageMultiple` | Nullable numeric ratio, don't summarize | October quantity / that subscription's unrounded Jan-Sep average; not a percentage |
| `UsageSpikeFlag` | Whole number 0/1 | October usage more than 5x a positive Jan-Sep baseline; zero in other months |
| `CreditReason` | Text, nullable | Distinct credit reason codes joined with semicolons; blank when no credit |
| `DMSWithoutAuctionFlag` | Whole number 0/1 | Entitled DMS contract for an active dealership with no entitled Auction Access contract at month end |

Dates, numeric amounts, and flags must load with appropriate types. The Lakehouse loader infers types; inspect them rather than assuming success. Null baseline/multiple values mean **not applicable**, not zero usage or zero risk. Ratios are stored to six decimals and discount fractions to eight; display to two decimals. Formatting doesn't restore fixed-precision currency.

## Rules that prevent misleading answers

- **Billing vs MRR:** `NetBilled` is signed billed charges, not cash collected or recognized accounting revenue. `ContractMRR` is a month-end run rate, not billed revenue.
- **Snapshot vs flow:** don't sum MRR, contract rates, or entitled counts across months. A historical count of distinct `SubscriptionID` is not a current entitled count.
- **Entitlement:** StartDate <= month end and EndDate blank or >= month end. Current contract status isn't used as historical status.
- **Overlaps:** both contracts in a duplicate pair are flagged. Sum of the overlap flag counts flagged contracts, not duplicate dealer/product pairs. Suspected excess assumes one contract was intended; confirm commercially before acting.
- **Post-end charges:** these compare service month starts, not invoice dates. The planted case ends on a month boundary; this isn't a general proration engine.
- **Usage:** baseline is fixed Jan-Sep for October only; missing monthly usage contributes zero to that nine-month average. Never aggregate different unit types or sum per-contract multiples.
- **Discounts:** negotiated rates and list prices are reference values repeated over months. Use one entitled monthly snapshot to estimate a monthly concession.
- **Cross-sell:** filter one month and `DMSWithoutAuctionFlag = 1`, then count distinct dealerships. There is one eligible DMS contract per candidate in this file. Price opportunity uses Auction Access list price **$149/month**, not the selected DMS price; it isn't a forecast.
- **Review candidates:** anomaly metrics are precomputed teaching aids, not proof of wrongdoing, approved refunds, or causal explanations. No machine-learning anomaly detection is performed.

The fixed reporting date is **November 3, 2026**, with January-October history in USD. Dealerships, service labels, contracts, and prices are synthetic. No invoice identifiers, payment attempts, outstanding balances, overdue measures, taxes, margins, or approval history are included. Don't try to answer the full workshop's collections questions from this table.

For production, retain governed transaction detail, explicit measures, appropriate dimensional/date modeling, precise currency types, security, and refresh logic. Express intentionally trades that breadth for one upload and straightforward questions.
