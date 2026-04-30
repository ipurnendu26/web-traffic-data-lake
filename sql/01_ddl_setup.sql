-- 1. Create the curated database
CREATE DATABASE logs_curated_db;

-- 2. Create the External Table pointing to the Parquet files in S3
-- IMPORTANT: Replace <your-bucket-name> with your actual bucket name!
CREATE EXTERNAL TABLE logs_curated_db.web_logs_curated (
  event_ts timestamp,
  log_date date,
  user_id string,
  session_id string,
  url_path string,
  http_status int,
  response_ms int,
  country string,
  device_type string,
  status_class string,
  response_bucket string
)
PARTITIONED BY (year int, month int, day int)
STORED AS PARQUET
LOCATION 's3://<your-bucket-name>/curated/web_logs_by_date/'
tblproperties ("parquet.compress"="SNAPPY");

-- 3. Load the partitions (Run this after the Glue Job finishes successfully)
MSCK REPAIR TABLE logs_curated_db.web_logs_curated;