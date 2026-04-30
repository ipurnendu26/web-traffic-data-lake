# Serverless Web Traffic Data Lake & Security Governance Platform 📌

## Project Overview

This project demonstrates the end-to-end implementation of a Modern Data Lake Architecture on AWS. It transforms raw, unstructured web server logs into structured, queryable business intelligence while enforcing Fine-Grained Access Control (FGAC) for data privacy.

The architecture follows the **Medallion Architecture** (Raw → Curated) and utilizes a fully serverless stack to minimize operational overhead and maximize scalability.

## 🏗️ Architecture

- **Storage**: Amazon S3 (Raw and Curated layers)
- **Orchestration & ETL**: AWS Glue (PySpark) for data cleaning, normalization, and partitioning
- **Metadata Management**: AWS Glue Data Catalog
- **Security & Governance**: AWS Lake Formation (Data Cell Access Control)
- **Analytics**: Amazon Athena (SQL)
- **Monitoring**: Amazon CloudWatch (Logs & Metrics)
- **Visualization**: Microsoft Excel / Amazon QuickSight

## 🚀 Key Features

### 1. Automated ETL Pipeline (PySpark)

The Glue ETL job performs the following transformations:

- **Data Cleaning**: Filters malformed HTTP status codes and negative response times
- **Normalization**: Standardizes timestamps, trims whitespace, and converts URLs to lower-case
- **Schema Enrichment**: Derives `status_class` (2xx, 4xx, 5xx) and `response_bucket` (FAST, MEDIUM, SLOW) for enhanced analytical depth
- **Performance Optimization**: Data is converted from CSV to Snappy-compressed Parquet and partitioned by year/month/day to reduce Athena query costs

### 2. Advanced Security & PII Masking

Implemented Data Cell Access Control (DCAC) via AWS Lake Formation. This ensures that:

- **Administrators** see the full dataset
- **Product Analysts** are restricted by a Data Filter that masks sensitive PII columns (`user_id`, `session_id`) while maintaining access to non-sensitive analytical fields

### 3. Operational Monitoring

Integrated CloudWatch for proactive system health tracking, including:

- **Job Metrics**: Tracking `total_input_rows` vs. `total_output_rows`
- **Alarms**: Configured SNS notifications for failed ETL job runs

## 📊 Business Insights

Based on the analysis of 1,000+ generated log entries, the following insights were derived:

- **Data Integrity**: Successfully processed 1,005 logs with a 99.6% quality score (4 rows dropped due to malformation)
- **System Reliability**: Detected a server error rate (5xx) of 4.4% during peak traffic periods
  
  $$\text{Error Rate} = \left( \frac{\sum \text{5xx Errors}}{\text{Total Requests}} \right) \times 100$$

- **Performance**: ~65% of requests were categorized as "SLOW," indicating a potential bottleneck in the simulated application backend
- **Traffic Peak**: Identified peak user activity at 12:00 PM on May 2nd, 2026

## 📂 Repository Structure

```
web-traffic-data-lake/
├── data/
│   ├── raw/
│   │   └── messy_logs_batch1.csv
├── scripts/
│   ├── generate_logs.py              # Script to generate messy synthetic logs
│   └── web_logs_curator.py           # PySpark ETL script for AWS Glue
├── sql/
│   ├── 01_ddl_setup.sql             # DDL for database setup
│   └── 02_analytics.sql             # Analytical queries
├── requirements.txt
└── README.md
```

## 🛠️ How to Deploy

### Local Setup

1. Create and activate a virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate synthetic raw logs:
   ```bash
   python scripts/generate_logs.py --rows 200000
   ```

### AWS Flow (Glue + Athena)

1. **Ingestion**: Upload `messy_logs_batch1.csv` to your S3 raw bucket
2. **Discovery**: Run the AWS Glue Crawler to populate the `web_traffic_raw_db`
3. **Transformation**: Run `glue_etl_job.py` in AWS Glue, passing the bucket name as a parameter:
   - `--INPUT_PATH s3://YOUR_BUCKET/raw/`
   - `--OUTPUT_PATH s3://YOUR_BUCKET/curated/`
4. **Governance**: Configure Lake Formation Data Filters to mask PII for restricted IAM roles
5. **Analytics**: Execute `athena_queries.sql` to generate curated views and export results for visualization

## 📋 Notes

- Replace `YOUR_BUCKET` with your real S3 bucket name in SQL and Glue job arguments
- `data/raw/messy_logs_batch1.csv` is ignored in Git to keep the repository lightweight
- Ensure proper IAM roles are configured for Glue, Athena, and Lake Formation services

