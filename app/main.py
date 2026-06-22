import logging
from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
)

app = FastAPI(title="DataOps App")


@app.get("/health")
def health():
    logging.info("Health check requested")
    return {"status": "ok"}


@app.get("/summary")
def summary():
    logging.info("Summary endpoint requested")
    return {
        "pipeline": "dataops_sales_pipeline",
        "status": "available",
        "description": "Simple API deployed on local Kubernetes"
    }