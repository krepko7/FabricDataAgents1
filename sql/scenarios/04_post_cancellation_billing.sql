-- Q04: Recurring service billed strictly after the inclusive contract end date.
SELECT d.DealershipName, p.ProductName, s.EndDate,
       COUNT(*) AS IncorrectCharges, SUM(l.LineAmount) AS BilledAfterEnd
FROM dbo.InvoiceLines l
JOIN dbo.Invoices i ON i.InvoiceID = l.InvoiceID
JOIN dbo.Subscriptions s ON s.SubscriptionID = l.SubscriptionID
JOIN dbo.Dealerships d ON d.DealershipID = s.DealershipID
JOIN dbo.Products p ON p.ProductID = s.ProductID
WHERE i.InvoiceStatus = 'Issued' AND s.EndDate IS NOT NULL
  AND l.ServiceMonth > s.EndDate AND l.LineType = 'Recurring'
GROUP BY d.DealershipName, p.ProductName, s.EndDate
ORDER BY BilledAfterEnd DESC, d.DealershipName;
