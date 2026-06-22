import logging
from datetime import datetime

import pandas as pd
import psycopg2


logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
)

DB_CONFIG = {
    "host": "postgres",
    "database": "dataops",
    "user": "dataops",
    "password": "dataops",
    "port": 5432,
}


def run_pipeline():
    logging.info("Starting DataOps pipeline")

    df = pd.read_csv("/opt/airflow/data/sales.csv")
    logging.info(f"Extracted {len(df)} rows")

    df["total"] = df["quantity"] * df["price"]
    df["processed_at"] = datetime.utcnow()
    logging.info("Data transformed successfully")

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales_processed (
            id INTEGER PRIMARY KEY,
            store TEXT,
            product TEXT,
            quantity INTEGER,
            price NUMERIC,
            total NUMERIC,
            processed_at TIMESTAMP
        );
    """)

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO sales_processed
            (id, store, product, quantity, price, total, processed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                store = EXCLUDED.store,
                product = EXCLUDED.product,
                quantity = EXCLUDED.quantity,
                price = EXCLUDED.price,
                total = EXCLUDED.total,
                processed_at = EXCLUDED.processed_at;
        """, (
            int(row["id"]),
            row["store"],
            row["product"],
            int(row["quantity"]),
            float(row["price"]),
            float(row["total"]),
            row["processed_at"],
        ))

    conn.commit()
    cursor.close()
    conn.close()

    logging.info("Data loaded successfully into PostgreSQL")


if __name__ == "__main__":
    run_pipeline()