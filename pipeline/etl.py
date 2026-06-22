import logging
from datetime import datetime

import pandas as pd
import psycopg2


# Configuração de logs estruturados em formato JSON
# Facilita a observabilidade e a integração com ferramentas de monitorização
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
)


# Configuração da ligação ao PostgreSQL
# O hostname "postgres" corresponde ao nome do serviço definido no docker-compose.yml
DB_CONFIG = {
    "host": "postgres",
    "database": "dataops",
    "user": "dataops",
    "password": "dataops",
    "port": 5432,
}


def run_pipeline():
    logging.info("Starting DataOps pipeline")

    # ETAPA 1 — EXTRAÇÃO (Extract)
    # Leitura do ficheiro CSV montado no container do Airflow
    df = pd.read_csv("/opt/airflow/data/sales.csv")

    logging.info(f"Extracted {len(df)} rows")

    # ETAPA 2 — TRANSFORMAÇÃO (Transform)
    # Cálculo do valor total por registo
    df["total"] = df["quantity"] * df["price"]

    # Adição do timestamp de processamento
    df["processed_at"] = datetime.utcnow()

    logging.info("Data transformed successfully")

    # ETAPA 3 — CARGA (Load)
    # Ligação ao PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Criação da tabela caso ainda não exista
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

    # Inserção ou atualização dos dados processados
    # ON CONFLICT garante idempotência da execução
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

    # Confirma as alterações na base de dados
    conn.commit()

    # Fecha a ligação e liberta recursos
    cursor.close()
    conn.close()

    logging.info("Data loaded successfully into PostgreSQL")


# Permite executar o pipeline diretamente pela linha de comandos
if __name__ == "__main__":
    run_pipeline()