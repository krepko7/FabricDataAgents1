-- Run against the Azure SQL source after loading. Read-only and assertion-based.
SET NOCOUNT ON;

IF (SELECT COUNT(*) FROM dbo.Dealerships) <> 24
    THROW 50010, 'Expected 24 dealerships.', 1;
IF (SELECT COUNT(*) FROM dbo.Products) <> 7
    THROW 50010, 'Expected 7 products.', 1;
IF (SELECT COUNT(*) FROM dbo.Subscriptions) <> 127
    THROW 50010, 'Expected 127 subscriptions.', 1;
IF (SELECT COUNT(*) FROM dbo.UsageRecords) <> 540
    THROW 50010, 'Expected 540 usage records.', 1;
IF (SELECT COUNT(*) FROM dbo.Invoices) <> 240
    THROW 50010, 'Expected 240 invoices.', 1;
IF (SELECT COUNT(*) FROM dbo.InvoiceLines) <> 1797
    THROW 50010, 'Expected 1797 invoice lines.', 1;
IF (SELECT COUNT(*) FROM dbo.Payments) <> 242
    THROW 50010, 'Expected 242 baseline payment attempts; live demo changes this count.', 1;

IF EXISTS (
    SELECT i.InvoiceID FROM dbo.Invoices i
    LEFT JOIN dbo.InvoiceLines l ON l.InvoiceID = i.InvoiceID
    GROUP BY i.InvoiceID, i.TotalAmount
    HAVING i.TotalAmount <> COALESCE(SUM(l.LineAmount), 0)
)
    THROW 50011, 'Invoice totals do not reconcile to lines.', 1;

IF EXISTS (
    SELECT 1 FROM dbo.InvoiceLines l
    JOIN dbo.Invoices i ON i.InvoiceID = l.InvoiceID
    JOIN dbo.Subscriptions s ON s.SubscriptionID = l.SubscriptionID
    WHERE i.DealershipID <> s.DealershipID OR i.BillingMonth <> l.ServiceMonth
)
    THROW 50012, 'Invoice line customer or service month mismatch.', 1;

IF EXISTS (
    SELECT i.InvoiceID FROM dbo.Invoices i
    JOIN dbo.Payments p ON p.InvoiceID = i.InvoiceID
    WHERE p.PaymentStatus = 'Succeeded'
    GROUP BY i.InvoiceID, i.TotalAmount
    HAVING SUM(p.Amount) > i.TotalAmount
)
    THROW 50013, 'Successful collections exceed an invoice total.', 1;

IF COALESCE((SELECT SUM(LineAmount) FROM dbo.InvoiceLines
    WHERE SubscriptionID = 1201 AND ServiceMonth > '2026-08-31'), 0) <> 398
    THROW 50014, 'Cancelled subscription billing fixture is missing.', 1;
IF COALESCE((SELECT Quantity FROM dbo.UsageRecords
    WHERE SubscriptionID = 907 AND UsageMonth = '2026-10-01'), 0) <> 2400
    THROW 50014, 'Usage spike fixture is missing.', 1;
IF (SELECT COUNT(*) FROM dbo.Payments WHERE PaymentStatus = 'Failed') <> 6
    THROW 50014, 'Expected six failed attempts, not six unpaid invoices.', 1;
IF COALESCE((SELECT SUM(LineAmount) FROM dbo.InvoiceLines WHERE LineType = 'Credit'), 0) <> -300
    THROW 50014, 'Expected one service credit of -300 USD.', 1;

SELECT 'Dealerships' AS TableName, COUNT(*) AS [RowCount] FROM dbo.Dealerships
UNION ALL SELECT 'Products', COUNT(*) FROM dbo.Products
UNION ALL SELECT 'Subscriptions', COUNT(*) FROM dbo.Subscriptions
UNION ALL SELECT 'UsageRecords', COUNT(*) FROM dbo.UsageRecords
UNION ALL SELECT 'Invoices', COUNT(*) FROM dbo.Invoices
UNION ALL SELECT 'InvoiceLines', COUNT(*) FROM dbo.InvoiceLines
UNION ALL SELECT 'Payments', COUNT(*) FROM dbo.Payments;

SELECT 'PASS: source reconciliation and planted anomaly checks' AS ValidationResult;
