-- Q01: October net billed revenue by product and charge type (USD, not cash).
SELECT p.ProductName,
       SUM(CASE WHEN l.LineType = 'Recurring' THEN l.LineAmount ELSE 0 END) AS RecurringBilled,
       SUM(CASE WHEN l.LineType = 'Usage' THEN l.LineAmount ELSE 0 END) AS UsageBilled,
       SUM(CASE WHEN l.LineType = 'Credit' THEN l.LineAmount ELSE 0 END) AS Credits,
       SUM(l.LineAmount) AS NetBilled
FROM dbo.InvoiceLines l
JOIN dbo.Subscriptions s ON s.SubscriptionID = l.SubscriptionID
JOIN dbo.Products p ON p.ProductID = s.ProductID
JOIN dbo.Invoices i ON i.InvoiceID = l.InvoiceID
WHERE l.ServiceMonth = '2026-10-01' AND i.InvoiceStatus = 'Issued'
GROUP BY p.ProductName
ORDER BY NetBilled DESC, p.ProductName;
