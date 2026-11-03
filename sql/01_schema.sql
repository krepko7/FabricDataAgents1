-- Run only against a dedicated, empty demo database. Never drops existing objects.
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF EXISTS (
    SELECT 1 FROM sys.tables
    WHERE schema_id = SCHEMA_ID('dbo')
      AND name IN ('Dealerships', 'Products', 'Subscriptions', 'UsageRecords',
                   'Invoices', 'InvoiceLines', 'Payments')
)
    THROW 50001, 'Demo tables already exist. Use a new empty database; no data was removed.', 1;

BEGIN TRY
    BEGIN TRANSACTION;

    CREATE TABLE dbo.Dealerships (
        DealershipID int NOT NULL PRIMARY KEY,
        DealershipName nvarchar(100) NOT NULL,
        DealerGroup nvarchar(80) NOT NULL,
        City nvarchar(60) NOT NULL,
        StateCode char(2) NOT NULL,
        Region varchar(20) NOT NULL,
        AccountStatus varchar(20) NOT NULL CHECK (AccountStatus IN ('Active', 'Inactive')),
        JoinedDate date NOT NULL,
        BillingEmail varchar(120) NOT NULL UNIQUE,
        PaymentTermsDays int NOT NULL CHECK (PaymentTermsDays BETWEEN 0 AND 90)
    );

    CREATE TABLE dbo.Products (
        ProductID int NOT NULL PRIMARY KEY,
        ProductCode varchar(30) NOT NULL UNIQUE,
        ProductName nvarchar(100) NOT NULL,
        Category varchar(40) NOT NULL,
        MonthlyListPrice decimal(12,2) NOT NULL CHECK (MonthlyListPrice >= 0),
        IncludedUnits int NOT NULL CHECK (IncludedUnits >= 0),
        OverageUnitPrice decimal(12,2) NOT NULL CHECK (OverageUnitPrice >= 0),
        UsageUnit varchar(30) NOT NULL
    );

    CREATE TABLE dbo.Subscriptions (
        SubscriptionID int NOT NULL PRIMARY KEY,
        DealershipID int NOT NULL REFERENCES dbo.Dealerships(DealershipID),
        ProductID int NOT NULL REFERENCES dbo.Products(ProductID),
        StartDate date NOT NULL,
        EndDate date NULL,
        SubscriptionStatus varchar(20) NOT NULL
            CHECK (SubscriptionStatus IN ('Active', 'Cancelled', 'Suspended')),
        MonthlyRate decimal(12,2) NOT NULL CHECK (MonthlyRate >= 0),
        IncludedUnits int NOT NULL CHECK (IncludedUnits >= 0),
        OverageUnitPrice decimal(12,2) NOT NULL CHECK (OverageUnitPrice >= 0),
        ContractReference varchar(40) NOT NULL UNIQUE,
        CHECK (EndDate IS NULL OR EndDate >= StartDate),
        CHECK ((SubscriptionStatus = 'Active' AND EndDate IS NULL)
            OR (SubscriptionStatus <> 'Active' AND EndDate IS NOT NULL))
    );

    CREATE TABLE dbo.UsageRecords (
        UsageRecordID int NOT NULL PRIMARY KEY,
        SubscriptionID int NOT NULL REFERENCES dbo.Subscriptions(SubscriptionID),
        UsageMonth date NOT NULL,
        Quantity int NOT NULL CHECK (Quantity >= 0),
        RecordedAt datetime2(0) NOT NULL,
        UNIQUE (SubscriptionID, UsageMonth),
        CHECK (DAY(UsageMonth) = 1)
    );

    CREATE TABLE dbo.Invoices (
        InvoiceID int NOT NULL PRIMARY KEY,
        InvoiceNumber varchar(30) NOT NULL UNIQUE,
        DealershipID int NOT NULL REFERENCES dbo.Dealerships(DealershipID),
        BillingMonth date NOT NULL,
        InvoiceDate date NOT NULL,
        DueDate date NOT NULL,
        CurrencyCode char(3) NOT NULL CHECK (CurrencyCode = 'USD'),
        InvoiceStatus varchar(20) NOT NULL CHECK (InvoiceStatus IN ('Issued', 'Void')),
        TotalAmount decimal(12,2) NOT NULL CHECK (TotalAmount >= 0),
        UNIQUE (DealershipID, BillingMonth),
        CHECK (DAY(BillingMonth) = 1),
        CHECK (DueDate >= InvoiceDate)
    );

    CREATE TABLE dbo.InvoiceLines (
        InvoiceLineID int NOT NULL PRIMARY KEY,
        InvoiceID int NOT NULL REFERENCES dbo.Invoices(InvoiceID),
        SubscriptionID int NOT NULL REFERENCES dbo.Subscriptions(SubscriptionID),
        ServiceMonth date NOT NULL,
        LineType varchar(20) NOT NULL CHECK (LineType IN ('Recurring', 'Usage', 'Credit')),
        Quantity int NOT NULL CHECK (Quantity > 0),
        UnitPrice decimal(12,2) NOT NULL,
        LineAmount decimal(12,2) NOT NULL,
        ReasonCode varchar(30) NOT NULL,
        CHECK (DAY(ServiceMonth) = 1),
        CHECK (LineAmount = Quantity * UnitPrice),
        CHECK ((LineType = 'Credit' AND UnitPrice < 0)
            OR (LineType <> 'Credit' AND UnitPrice >= 0))
    );

    CREATE TABLE dbo.Payments (
        PaymentID int NOT NULL PRIMARY KEY,
        InvoiceID int NOT NULL REFERENCES dbo.Invoices(InvoiceID),
        PaymentDate date NOT NULL,
        Amount decimal(12,2) NOT NULL CHECK (Amount > 0),
        PaymentStatus varchar(20) NOT NULL CHECK (PaymentStatus IN ('Succeeded', 'Failed')),
        PaymentMethod varchar(20) NOT NULL CHECK (PaymentMethod IN ('ACH', 'Card')),
        FailureCode varchar(40) NULL,
        ProcessorReference varchar(50) NOT NULL UNIQUE,
        CHECK ((PaymentStatus = 'Failed' AND FailureCode IS NOT NULL)
            OR (PaymentStatus = 'Succeeded' AND FailureCode IS NULL))
    );

    CREATE INDEX IX_Subscriptions_DealerProduct
        ON dbo.Subscriptions(DealershipID, ProductID);
    CREATE INDEX IX_InvoiceLines_Invoice ON dbo.InvoiceLines(InvoiceID);
    CREATE INDEX IX_InvoiceLines_SubscriptionMonth
        ON dbo.InvoiceLines(SubscriptionID, ServiceMonth);
    CREATE INDEX IX_Payments_Invoice ON dbo.Payments(InvoiceID);

    COMMIT;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    THROW;
END CATCH;
