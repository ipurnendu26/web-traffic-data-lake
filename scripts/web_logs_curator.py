import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, to_timestamp, to_date, when, lower, trim, split, year, month, dayofmonth
from awsglue.dynamicframe import DynamicFrame

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

bucket = args['BUCKET_NAME']

# 1. Read from Curated (Note updated DB name)
dyf_raw = glueContext.create_dynamic_frame.from_catalog(
    database="web_traffic_raw_db", 
    table_name="web_logs",
    transformation_ctx="read_raw_logs"
)
df = dyf_raw.toDF()
total_input_rows = df.count()

# 2. Cleaning
df_clean = df.drop("extra_param1", "extra_param2")
df_clean = df_clean.withColumn("http_status", col("http_status").cast("int")) \
                   .withColumn("response_ms", col("response_ms").cast("int"))

df_clean = df_clean.filter(
    col("http_status").isNotNull() & (col("http_status").between(100, 599)) &
    col("response_ms").isNotNull() & (col("response_ms") >= 0) & (col("response_ms") <= 60000)
)

# 3. Normalization
df_norm = df_clean.withColumn("event_ts", to_timestamp(col("event_ts"))) \
                  .filter(col("event_ts").isNotNull()) \
                  .withColumn("log_date", to_date(col("event_ts"))) \
                  .withColumn("country", trim(lower(col("country")))) \
                  .withColumn("device_type", trim(lower(col("device_type")))) \
                  .withColumn("url_path", split(col("url_path"), "\\?").getItem(0))

# 4. Enrichment
df_enriched = df_norm.withColumn("status_class", 
                        when(col("http_status") < 300, "2xx")
                        .when(col("http_status") < 400, "3xx")
                        .when(col("http_status") < 500, "4xx")
                        .otherwise("5xx")) \
                     .withColumn("response_bucket",
                        when(col("response_ms") < 200, "FAST")
                        .when(col("response_ms") <= 1000, "MEDIUM")
                        .otherwise("SLOW")) \
                     .withColumn("year", year(col("log_date"))) \
                     .withColumn("month", month(col("log_date"))) \
                     .withColumn("day", dayofmonth(col("log_date")))

total_output_rows = df_enriched.count()

# 5. Metrics Tracking
dropped_rows = total_input_rows - total_output_rows
profiling_data = [("total_input_rows", total_input_rows), 
                  ("total_output_rows", total_output_rows), 
                  ("dropped_rows", dropped_rows)]
df_profile = spark.createDataFrame(profiling_data, ["metric", "value"])
df_profile.coalesce(1).write.mode("overwrite").csv(f"s3://{bucket}/curated/metrics/job_run_stats/", header=True)

# 6. Write Curated Parquet
dyf_curated = DynamicFrame.fromDF(df_enriched, glueContext, "dyf_curated")
glueContext.write_dynamic_frame.from_options(
    frame=dyf_curated,
    connection_type="s3",
    connection_options={
        "path": f"s3://{bucket}/curated/web_logs_by_date/", 
        "partitionKeys": ["year", "month", "day"]
    },
    format="parquet",
    format_options={"compression": "snappy"}
)

job.commit()