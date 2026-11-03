-- Q09: Retries vs affected invoices; count each outstanding invoice only once.
WITH Attempts AS (
    SELECT InvoiceID, COUNT(*) AS FailedAttempts
    FROM dbo.Payments
    WHERE PaymentStatus = 'Failed' AND PaymentDate <= '2026-11-03'
    GROUP BY InvoiceID
), Collections AS (
    SELECT InvoiceID, SUM(Amount) AS Collected
    FROM dbo.Payments
    WHERE PaymentStatus = 'Succeeded' AND PaymentDate <= '2026-11-03'
    GROUP BY InvoiceID
)
SELECT d.DealershipName, SUM(a.FailedAttempts) AS FailedAttempts,
       COUNT(*) AS AffectedInvoices,
       SUM(i.TotalAmount - COALESCE(c.Collected, 0)) AS OutstandingBalance
FROM Attempts a
JOIN dbo.Invoices i ON i.InvoiceID = a.InvoiceID
JOIN dbo.Dealerships d ON d.DealershipID = i.DealershipID
LEFT JOIN Collections c ON c.InvoiceID = i.InvoiceID
WHERE i.InvoiceStatus = 'Issued'
GROUP BY d.DealershipName
ORDER BY FailedAttempts DESC, d.DealershipName;
