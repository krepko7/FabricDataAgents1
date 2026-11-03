-- Q11: Signed service credits, by dealer and product in September.
SELECT d.DealershipName, p.ProductName, l.ReasonCode,
       SUM(l.LineAmount) AS CreditAmount
FROM dbo.InvoiceLines l
JOIN dbo.Invoices i ON i.InvoiceID = l.InvoiceID
JOIN dbo.Subscriptions s ON s.SubscriptionID = l.SubscriptionID
JOIN dbo.Dealerships d ON d.DealershipID = s.DealershipID
JOIN dbo.Products p ON p.ProductID = s.ProductID
WHERE i.InvoiceStatus = 'Issued' AND l.LineType = 'Credit'
  AND l.ServiceMonth = '2026-09-01'
GROUP BY d.DealershipName, p.ProductName, l.ReasonCode
ORDER BY CreditAmount, d.DealershipName;
