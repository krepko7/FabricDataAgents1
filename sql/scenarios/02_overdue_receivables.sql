-- Q02: Past-due balances as of 2026-11-03, after successful payments only.
WITH Collections AS (
    SELECT InvoiceID, SUM(Amount) AS Collected
    FROM dbo.Payments
    WHERE PaymentStatus = 'Succeeded' AND PaymentDate <= '2026-11-03'
    GROUP BY InvoiceID
)
SELECT d.DealershipName, COUNT(*) AS OverdueInvoices,
       SUM(i.TotalAmount - COALESCE(c.Collected, 0)) AS OverdueBalance
FROM dbo.Invoices i
JOIN dbo.Dealerships d ON d.DealershipID = i.DealershipID
LEFT JOIN Collections c ON c.InvoiceID = i.InvoiceID
WHERE i.InvoiceStatus = 'Issued' AND i.InvoiceDate <= '2026-11-03'
  AND i.DueDate < '2026-11-03'
  AND i.TotalAmount > COALESCE(c.Collected, 0)
GROUP BY d.DealershipName
ORDER BY OverdueBalance DESC, d.DealershipName;
