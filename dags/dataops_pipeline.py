from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

import sys

# Adiciona o diretório base do Airflow ao PATH do Python
# Permite importar módulos personalizados da pasta pipeline/
sys.path.append("/opt/airflow")

from pipeline.etl import run_pipeline


# Definição da DAG (Directed Acyclic Graph)
# A DAG representa o fluxo de orquestração do pipeline
with DAG(
    dag_id="dataops_sales_pipeline",
    description="Simple DataOps pipeline for Involves technical challenge",

    # Data de início da DAG
    # Como o schedule está desativado, esta data serve apenas como referência
    start_date=datetime(2026, 1, 1),

    # Execução manual através da interface do Airflow
    schedule=None,

    # Impede a execução retroativa de intervalos anteriores
    catchup=False,

    # Tags para facilitar a organização e pesquisa na interface
    tags=["dataops", "involves"],
) as dag:

    # Definição da tarefa que executa o pipeline ETL
    run_sales_pipeline = PythonOperator(

        # Nome da tarefa apresentado na interface do Airflow
        task_id="run_sales_pipeline",

        # Função Python responsável por executar o pipeline
        python_callable=run_pipeline,
    )