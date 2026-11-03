-- Q05: October meter quantity greater than 5x its Jan-Sep monthly average.
WITH Baseline AS (
    SELECT SubscriptionID, AVG(CAST(Quantity AS decimal(12,2))) AS AverageQuantity
    FROM dbo.UsageRecords
    WHERE UsageMonth >= '2026-01-01' AND UsageMonth < '2026-10-01'
    GROUP BY SubscriptionID
)
SELECT d.DealershipName, p.ProductName, u.Quantity AS OctoberQuantity,
       ROUND(b.AverageQuantity, 2) AS BaselineQuantity,
       ROUND(u.Quantity / NULLIF(b.AverageQuantity, 0), 2) AS BaselineMultiple,
       (u.Quantity - s.IncludedUnits) * s.OverageUnitPrice AS ExpectedOverage
FROM dbo.UsageRecords u
JOIN Baseline b ON b.SubscriptionID = u.SubscriptionID
JOIN dbo.Subscriptions s ON s.SubscriptionID = u.SubscriptionID
JOIN dbo.Dealerships d ON d.DealershipID = s.DealershipID
JOIN dbo.Products p ON p.ProductID = s.ProductID
WHERE u.UsageMonth = '2026-10-01' AND u.Quantity > 5 * b.AverageQuantity
ORDER BY BaselineMultiple DESC, d.DealershipName;
