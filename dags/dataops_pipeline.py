from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
sys.path.append("/opt/airflow")

from pipeline.etl import run_pipeline


with DAG(
    dag_id="dataops_sales_pipeline",
    description="Simple DataOps pipeline for Involves technical challenge",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["dataops", "involves"],
) as dag:

    run_sales_pipeline = PythonOperator(
        task_id="run_sales_pipeline",
        python_callable=run_pipeline,
    )