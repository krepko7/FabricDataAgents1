-- Q10: Point-in-time entitled recurring run rate; not actual invoice revenue.
WITH Snapshots AS (
    SELECT CAST('2026-09-30' AS varchar(10)) AS SnapshotDate
    UNION ALL SELECT CAST('2026-10-31' AS varchar(10))
)
SELECT x.SnapshotDate, COUNT(*) AS EntitledSubscriptions,
       SUM(s.MonthlyRate) AS ContractMRR
FROM Snapshots x
JOIN dbo.Subscriptions s ON s.StartDate <= x.SnapshotDate
    AND (s.EndDate IS NULL OR s.EndDate >= x.SnapshotDate)
GROUP BY x.SnapshotDate
ORDER BY x.SnapshotDate;
