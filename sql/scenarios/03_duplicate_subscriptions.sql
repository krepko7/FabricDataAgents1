-- Q03: More than one entitled contract per dealership/product on 2026-10-31.
SELECT d.DealershipName, p.ProductName, COUNT(*) AS ActiveContracts,
       SUM(s.MonthlyRate) AS ContractMRR,
       SUM(s.MonthlyRate) - MAX(s.MonthlyRate) AS SuspectedExcessMRR
FROM dbo.Subscriptions s
JOIN dbo.Dealerships d ON d.DealershipID = s.DealershipID
JOIN dbo.Products p ON p.ProductID = s.ProductID
WHERE s.StartDate <= '2026-10-31'
  AND (s.EndDate IS NULL OR s.EndDate >= '2026-10-31')
GROUP BY d.DealershipName, p.ProductName
HAVING COUNT(*) > 1
ORDER BY d.DealershipName, p.ProductName;
