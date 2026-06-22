# DataOps Technical Challenge

## Descrição

Solução desenvolvida para demonstrar uma plataforma DataOps composta por:

- Pipeline ETL em Python
- Apache Airflow para orquestração
- PostgreSQL para persistência de dados
- Aplicação FastAPI executada em Kubernetes local
- Pipeline de CI/CD com GitHub Actions

## Estrutura do Projeto

```text
.
├── app/
├── dags/
├── data/
├── k8s/
├── pipeline/
├── .github/
├── docker-compose.yml
├── requirements.txt
├── README.md
└── DECISIONS.md
```

## Execução do Ambiente de Dados

```bash
docker compose up -d
```

A interface do Airflow fica disponível em:

```text
http://localhost:8080
```

## Execução da Aplicação em Kubernetes

```bash
minikube start --driver=docker

eval $(minikube docker-env)

docker build -t dataops-app:local ./app

kubectl apply -f k8s/
```

Para validar a aplicação:

```bash
kubectl port-forward svc/dataops-app-service 8000:80
```

```bash
curl http://localhost:8000/health
curl http://localhost:8000/summary
```

## CI/CD

O projeto inclui um workflow de GitHub Actions executado automaticamente em:

- Push
- Pull Request
- Execução manual

## Documentação Técnica

As decisões de arquitetura e implementação encontram-se documentadas em:

- [DECISIONS.md](./DECISIONS.md)