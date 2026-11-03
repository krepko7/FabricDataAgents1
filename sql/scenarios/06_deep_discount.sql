-- Q06: Active contracts discounted at least 50% off monthly catalog list price.
SELECT d.DealershipName, p.ProductName, p.MonthlyListPrice, s.MonthlyRate,
       p.MonthlyListPrice - s.MonthlyRate AS MonthlyListGap,
       ROUND(100.0 * (p.MonthlyListPrice - s.MonthlyRate)
             / NULLIF(p.MonthlyListPrice, 0), 2) AS DiscountPercent
FROM dbo.Subscriptions s
JOIN dbo.Products p ON p.ProductID = s.ProductID
JOIN dbo.Dealerships d ON d.DealershipID = s.DealershipID
WHERE s.StartDate <= '2026-10-31'
  AND (s.EndDate IS NULL OR s.EndDate >= '2026-10-31')
  AND p.MonthlyListPrice > 0 AND s.MonthlyRate <= p.MonthlyListPrice * 0.5
ORDER BY MonthlyListGap DESC, d.DealershipName;
