-- Q07: October recurring unit price higher than the negotiated contract rate.
SELECT d.DealershipName, p.ProductName, i.InvoiceNumber,
       s.MonthlyRate AS ContractRate, l.UnitPrice AS BilledRate,
       l.LineAmount - l.Quantity * s.MonthlyRate AS Overcharge
FROM dbo.InvoiceLines l
JOIN dbo.Invoices i ON i.InvoiceID = l.InvoiceID
JOIN dbo.Subscriptions s ON s.SubscriptionID = l.SubscriptionID
JOIN dbo.Dealerships d ON d.DealershipID = s.DealershipID
JOIN dbo.Products p ON p.ProductID = s.ProductID
WHERE i.InvoiceStatus = 'Issued' AND l.ServiceMonth = '2026-10-01'
  AND l.LineType = 'Recurring' AND l.UnitPrice > s.MonthlyRate
ORDER BY Overcharge DESC, d.DealershipName;
