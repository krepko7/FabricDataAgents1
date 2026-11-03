-- OPTIONAL: run ONLY on Azure SQL after recording baseline scenario results.
-- Adds a real demo collection; does not change subscription or invoice history.
SET NOCOUNT ON;
SET XACT_ABORT ON;
BEGIN TRY
    BEGIN TRANSACTION;
    IF EXISTS (SELECT 1 FROM dbo.Payments WHERE ProcessorReference = 'DEMO-LIVE-804')
        THROW 50020, 'This demo payment was already applied; nothing was changed.', 1;

    DECLARE @Amount decimal(12,2);
    SELECT @Amount = i.TotalAmount - COALESCE((
        SELECT SUM(p.Amount) FROM dbo.Payments p
        WHERE p.InvoiceID = i.InvoiceID AND p.PaymentStatus = 'Succeeded'
    ), 0)
    FROM dbo.Invoices i WITH (UPDLOCK, HOLDLOCK)
    WHERE i.InvoiceID = 804 AND i.DealershipID = 4 AND i.InvoiceStatus = 'Issued';

    IF @Amount IS NULL OR @Amount <= 0
        THROW 50021, 'Expected an outstanding August invoice for Desert Mesa Motors.', 1;

    DECLARE @PaymentID int;
    SELECT @PaymentID = COALESCE(MAX(PaymentID), 0) + 1
    FROM dbo.Payments WITH (UPDLOCK, HOLDLOCK);

    INSERT INTO dbo.Payments
        (PaymentID, InvoiceID, PaymentDate, Amount, PaymentStatus, PaymentMethod,
         FailureCode, ProcessorReference)
    VALUES (@PaymentID, 804, '2026-11-03', @Amount, 'Succeeded', 'ACH', NULL, 'DEMO-LIVE-804');
    COMMIT;
    SELECT @Amount AS CollectedUSD, 'Desert Mesa Motors' AS DealershipName;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;
END CATCH;
