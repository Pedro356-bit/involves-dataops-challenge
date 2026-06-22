import logging
from fastapi import FastAPI


# Configuração de logs estruturados em formato JSON
# Facilita a leitura dos logs e futura integração com ferramentas de observabilidade
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
)


# Inicialização da aplicação FastAPI
app = FastAPI(title="DataOps App")


# Endpoint de health check
# Utilizado para validar se a aplicação está disponível
# Também será usado pelas probes do Kubernetes
@app.get("/health")
def health():
    logging.info("Health check requested")
    return {"status": "ok"}


# Endpoint simples de resumo da aplicação
# Permite validar que a API está a responder corretamente no Kubernetes
@app.get("/summary")
def summary():
    logging.info("Summary endpoint requested")
    return {
        "pipeline": "dataops_sales_pipeline",
        "status": "available",
        "description": "Simple API deployed on local Kubernetes"
    }