-- Query 1: Traffic Trend (Requests per hour)
SELECT 
    date_trunc('hour', event_ts) AS hour, 
    COUNT(*) as traffic
FROM logs_curated_db.web_logs_curated
GROUP BY 1 
ORDER BY 1;

-- Query 2: Top Pages by Traffic
SELECT 
    url_path, 
    COUNT(*) as visits
FROM logs_curated_db.web_logs_curated
GROUP BY 1 
ORDER BY 2 DESC 
LIMIT 5;

-- Query 3: Server Error Rate (5xx errors over time)
SELECT 
    log_date, 
    SUM(CASE WHEN status_class = '5xx' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS error_rate_pct
FROM logs_curated_db.web_logs_curated
GROUP BY 1 
ORDER BY 1;

-- Query 4: Response Time Bucket Distribution (Performance profiling)
SELECT 
    response_bucket, 
    COUNT(*) as count
FROM logs_curated_db.web_logs_curated
GROUP BY 1;