-- Q12: Active DMS customers with no entitled Auction Access contract on Oct 31.
SELECT d.DealershipName, d.Region,
       p.MonthlyListPrice AS PotentialMonthlyListRevenue
FROM dbo.Dealerships d
JOIN dbo.Products p ON p.ProductCode = 'AUCTION'
WHERE d.AccountStatus = 'Active'
  AND EXISTS (
    SELECT 1 FROM dbo.Subscriptions s
    JOIN dbo.Products owned ON owned.ProductID = s.ProductID
    WHERE s.DealershipID = d.DealershipID AND owned.ProductCode = 'DMS'
      AND s.StartDate <= '2026-10-31' AND (s.EndDate IS NULL OR s.EndDate >= '2026-10-31')
  )
  AND NOT EXISTS (
    SELECT 1 FROM dbo.Subscriptions s
    WHERE s.DealershipID = d.DealershipID AND s.ProductID = p.ProductID
      AND s.StartDate <= '2026-10-31' AND (s.EndDate IS NULL OR s.EndDate >= '2026-10-31')
  )
ORDER BY d.DealershipName;
