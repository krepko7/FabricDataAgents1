-- Q08: Positive October expected overage less issued usage charges.
WITH BilledUsage AS (
    SELECT l.SubscriptionID, l.ServiceMonth, SUM(l.LineAmount) AS BilledOverage
    FROM dbo.InvoiceLines l
    JOIN dbo.Invoices i ON i.InvoiceID = l.InvoiceID
    WHERE l.LineType = 'Usage' AND i.InvoiceStatus = 'Issued'
    GROUP BY l.SubscriptionID, l.ServiceMonth
)
SELECT d.DealershipName, p.ProductName, u.Quantity,
       s.IncludedUnits, s.OverageUnitPrice,
       (u.Quantity - s.IncludedUnits) * s.OverageUnitPrice AS ExpectedOverage,
       COALESCE(b.BilledOverage, 0) AS BilledOverage,
       (u.Quantity - s.IncludedUnits) * s.OverageUnitPrice
         - COALESCE(b.BilledOverage, 0) AS UnbilledOverage
FROM dbo.UsageRecords u
JOIN dbo.Subscriptions s ON s.SubscriptionID = u.SubscriptionID
JOIN dbo.Products p ON p.ProductID = s.ProductID
JOIN dbo.Dealerships d ON d.DealershipID = s.DealershipID
LEFT JOIN BilledUsage b ON b.SubscriptionID = u.SubscriptionID
                      AND b.ServiceMonth = u.UsageMonth
WHERE u.UsageMonth = '2026-10-01' AND u.Quantity > s.IncludedUnits
  AND (u.Quantity - s.IncludedUnits) * s.OverageUnitPrice > COALESCE(b.BilledOverage, 0)
ORDER BY UnbilledOverage DESC, d.DealershipName;
