"""
Spark Structured Streaming : agrégation H3 en temps réel.

Lecture des positions GPS depuis Kafka, indexation H3,
agrégation par hexagone + fenêtre temporelle.

Soumission:
  /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4 \
    h3_aggregation.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, count, approx_count_distinct, avg, udf
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType,
)

from h3_utils import lat_lon_to_h3

GPS_SCHEMA = StructType([
    StructField("vehicle_id", StringType()),
    StructField("type", StringType()),
    StructField("status", StringType()),
    StructField("timestamp", StringType()),
    StructField("lat", DoubleType()),
    StructField("lon", DoubleType()),
    StructField("altitude", DoubleType()),
    StructField("speed", DoubleType()),
    StructField("bearing", DoubleType()),
    StructField("battery", DoubleType()),
])

h3_udf = udf(lambda lat, lon: lat_lon_to_h3(float(lat), float(lon), 9), StringType())


def create_spark():
    return (
        SparkSession.builder
        .appName("h3-aggregation")
        .getOrCreate()
    )


def main():
    spark = create_spark()
    spark.sparkContext.setLogLevel("WARN")

    df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "gps-positions")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .option("maxOffsetsPerTrigger", "1000")
        .load()
        .select(from_json(col("value").cast("string"), GPS_SCHEMA).alias("gps"))
        .where(col("gps").isNotNull())
        .select("gps.*")
        .withColumn("event_time", col("timestamp").cast("timestamp"))
        .withColumn("h3_cell", h3_udf(col("lat"), col("lon")))
    )

    agg = (
        df.withWatermark("event_time", "30 seconds")
        .groupBy(
            window(col("event_time"), "1 minute"),
            col("h3_cell"),
            col("type"),
        )
        .agg(
            count("*").alias("num_points"),
            approx_count_distinct("vehicle_id").alias("unique_vehicles"),
            avg("speed").alias("avg_speed"),
        )
    )

    query = (
        agg.writeStream
        .outputMode("append")
        .format("console")
        .option("truncate", "false")
        .option("checkpointLocation", "/tmp/h3-checkpoints")
        .trigger(processingTime="15 seconds")
        .start()
    )

    print("H3 aggregation streaming started")
    query.awaitTermination()


if __name__ == "__main__":
    main()
