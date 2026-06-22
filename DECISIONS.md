## Visão Geral da Solução

A solução foi desenvolvida para demonstrar os principais componentes de uma plataforma DataOps moderna, incluindo orquestração de pipelines, processamento de dados, execução de aplicações containerizadas e automação do ciclo de entrega.

A arquitetura é composta pelos seguintes elementos:

- Ambiente local de dados com Docker Compose
- Pipeline ETL em Python
- Apache Airflow para orquestração
- PostgreSQL para persistência de dados
- Aplicação containerizada em Kubernetes local
- Pipeline de CI/CD com GitHub Actions
- Observabilidade básica através de logs estruturados e *health checks*

---

## 1. Ambiente Local de Dados

Responsável pela orquestração e execução do pipeline ETL.

### Componentes

- PostgreSQL
- Apache Airflow
  - `airflow-init`
  - `airflow-webserver`
  - `airflow-scheduler`
- Pipeline ETL em Python
- Ficheiro de entrada `sales.csv`

### Objetivos

- Disponibilizar um ambiente de desenvolvimento reproduzível
- Orquestrar a execução do pipeline de dados
- Processar e persistir os dados no PostgreSQL
- Permitir a monitorização da execução através da interface do Airflow

### Implementação com Docker Compose

Utilizei o Docker Compose para orquestrar localmente os serviços necessários ao desafio.

O ambiente é inicializado através do comando:

```bash
docker compose up -d
```

#### PostgreSQL

O PostgreSQL foi escolhido para armazenar:

- Os metadados do Airflow
- Os dados processados pelo pipeline ETL

Configurei um volume Docker para garantir a persistência dos dados entre reinicializações e um *health check* para assegurar que os serviços do Airflow apenas iniciam quando a base de dados está disponível.

#### Airflow Init

O serviço `airflow-init` é responsável pela preparação inicial do ambiente:

- Instalação das dependências Python
- Execução das migrações da base de dados
- Criação do utilizador administrador

#### Airflow Webserver

O serviço `airflow-webserver` disponibiliza a interface gráfica do Airflow na porta `8080`, permitindo visualizar, executar e monitorizar as DAGs.

#### Airflow Scheduler

O serviço `airflow-scheduler` monitoriza e executa as DAGs.

#### Volumes Partilhados

As pastas `dags/`, `pipeline/` e `data/` são montadas nos containers do Airflow para disponibilizar:

- DAGs
- Código do pipeline
- Dados de entrada

#### Fluxo de Execução

```text
docker compose up -d
        ↓
PostgreSQL inicia
        ↓
Health check valida a disponibilidade da base de dados
        ↓
airflow-init prepara o ambiente
        ↓
airflow-webserver disponibiliza a interface
        ↓
airflow-scheduler monitoriza as DAGs
        ↓
dataops_sales_pipeline executa o ETL
        ↓
sales.csv → PostgreSQL
```

### Pipeline ETL

O pipeline foi desenvolvido em Python seguindo o padrão ETL (*Extract, Transform, Load*).

#### Extract

Leitura do ficheiro `sales.csv` através do Pandas.

#### Transform

- Cálculo do valor total de cada venda
- Adição do *timestamp* de processamento

#### Load

Persistência dos dados no PostgreSQL utilizando `psycopg2`.

O pipeline utiliza `ON CONFLICT DO UPDATE` para garantir idempotência, evitando registos duplicados em execuções sucessivas.

Os logs são emitidos em formato JSON para facilitar a observabilidade.

### Orquestração com Airflow

Utilizei o Apache Airflow como orquestrador do pipeline de dados.

A solução foi implementada através de uma DAG denominada `dataops_sales_pipeline`, composta por uma única tarefa do tipo `PythonOperator`, responsável por executar o pipeline ETL.

#### Decisões adotadas

- `schedule=None` para execução manual durante a demonstração
- `catchup=False` para evitar execuções retroativas
- `LocalExecutor` para permitir maior paralelismo em ambiente local

Mantive uma separação clara entre:

- Orquestração: `dags/`
- Lógica de negócio: `pipeline/`

---

## 2. Aplicação Containerizada em Kubernetes

Responsável por demonstrar a execução e gestão de uma aplicação containerizada em Kubernetes local.

### Componentes

- Minikube
- Aplicação FastAPI
- Dockerfile
- Deployment Kubernetes
- Service Kubernetes
- *Health checks*
- Logs estruturados

### Objetivos

- Demonstrar o processo de containerização de uma aplicação
- Executar a aplicação num ambiente Kubernetes local
- Validar o funcionamento de *liveness probes* e *readiness probes*
- Expor endpoints para validação do *deploy*
- Demonstrar práticas básicas de observabilidade

### Aplicação FastAPI

Para cumprir o requisito do desafio de executar pelo menos uma peça da stack em Kubernetes, desenvolvi uma aplicação simples em FastAPI.

A aplicação expõe dois endpoints:

- `GET /health`
- `GET /summary`

A aplicação é *stateless* e emite logs estruturados em formato JSON.

### Papel do `app/main.py`

O ficheiro `app/main.py` contém a implementação da aplicação FastAPI executada no Kubernetes.

O seu principal objetivo é disponibilizar endpoints HTTP simples que permitam validar o funcionamento do *deploy* e demonstrar práticas básicas de observabilidade.

Foram implementados dois endpoints:

- `GET /health`: utilizado pelas *liveness probes* e *readiness probes* do Kubernetes para verificar se a aplicação está disponível e pronta para receber tráfego.
- `GET /summary`: disponibiliza informações resumidas sobre o pipeline implementado, permitindo validar o acesso à aplicação após o *deploy*.

Além dos endpoints, a aplicação está configurada para emitir logs estruturados em formato JSON, facilitando a integração futura com ferramentas de monitorização e centralização de logs.

A separação da aplicação na pasta `app/` permite manter o código da API desacoplado da lógica de processamento de dados.

### Containerização

A aplicação foi empacotada através de um `Dockerfile` localizado na pasta `app/`.

A imagem utiliza `python:3.12-slim` como base e é construída localmente através do comando:

```bash
docker build -t dataops-app:local ./app
```

Como o *deploy* é realizado em Minikube, a imagem é construída diretamente no ambiente Docker do cluster:

```bash
eval $(minikube docker-env)
```

Esta abordagem elimina a necessidade de utilizar um *registry* externo.

### Fluxo de Deploy

```bash
minikube start --driver=docker

eval $(minikube docker-env)

docker build -t dataops-app:local ./app

kubectl apply -f k8s/
```

### Fluxo de Execução

```text
app/main.py
    ↓
Dockerfile
    ↓
Imagem Docker dataops-app:local
    ↓
Deployment Kubernetes
    ↓
Pod
    ↓
Service
    ↓
Endpoints /health e /summary
```

---

## 3. Integração e Entrega Contínua (CI/CD)

Responsável por validar e empacotar a solução automaticamente.

### Componentes

- GitHub Actions
- Workflow de validação
- Build automatizado da imagem Docker

### Objetivos

- Validar automaticamente o código submetido
- Garantir a integridade da solução
- Automatizar o processo de empacotamento
- Assegurar a reprodutibilidade do ambiente

### Implementação com GitHub Actions

Foi criado um workflow de integração contínua através do GitHub Actions para validar automaticamente a solução.

O workflow é executado nos seguintes cenários:

- `push`: sempre que existe uma alteração no repositório
- `pull_request`: sempre que é criada ou atualizada uma *Pull Request*
- `workflow_dispatch`: execução manual através da interface do GitHub

### Workflow de Validação

O workflow executa um único *job*, denominado `validate-and-build`, utilizando um *runner* Ubuntu disponibilizado pelo GitHub.

Durante a execução, são realizados os seguintes passos:

#### 1. Checkout do Código

Obtém o conteúdo do repositório para o ambiente de execução do GitHub Actions.

#### 2. Configuração do Ambiente Python

Instala e configura a versão `3.12` do Python, garantindo consistência entre o ambiente local e o ambiente de CI.

#### 3. Instalação das Dependências do Pipeline ETL

Instala as dependências definidas no ficheiro `requirements.txt`, necessárias para a execução do pipeline de dados.

#### 4. Instalação das Dependências da Aplicação

Instala as dependências definidas no ficheiro `app/requirements.txt`, necessárias para a execução da aplicação FastAPI.

#### 5. Validação da Sintaxe Python

Executa o seguinte comando para validar a sintaxe dos ficheiros Python:

```bash
python -m compileall app pipeline dags
```

Este processo compila os ficheiros sem os executar, permitindo identificar erros de sintaxe antes do empacotamento da solução.

#### 6. Build da Imagem Docker

Executa o seguinte comando:

```bash
docker build -t dataops-app:ci ./app
```

O objetivo desta etapa é validar que o `Dockerfile` da aplicação está funcional e que a imagem pode ser construída com sucesso.

A imagem é criada temporariamente no ambiente do *runner* do GitHub e não é publicada num *registry* externo.

### Fluxo de Execução

```text
Push / Pull Request / Execução Manual
                    ↓
             Checkout do código
                    ↓
           Configuração do Python
                    ↓
     Instalação das dependências ETL
                    ↓
   Instalação das dependências da API
                    ↓
         Validação da sintaxe Python
                    ↓
            Build da imagem Docker
                    ↓
               Workflow concluído
```

### Considerações da Implementação

O pipeline de CI/CD foi desenhado para garantir que qualquer alteração submetida ao repositório seja automaticamente validada e que a aplicação possa ser empacotada com sucesso.

Nesta fase, o workflow executa apenas validações essenciais, mantendo o foco no objetivo principal do desafio.

---

## Decisões Técnicas

### O que foi escolhido

- Docker Compose para orquestração do ambiente local
- PostgreSQL como base de dados relacional
- Apache Airflow para orquestração do pipeline ETL
- `LocalExecutor` para execução local do Airflow
- Python para implementação da lógica de processamento de dados
- Pandas para transformação dos dados
- `psycopg2` para integração com PostgreSQL
- FastAPI para a aplicação demonstrativa
- Docker para containerização da aplicação
- Minikube para execução local do Kubernetes
- GitHub Actions para integração contínua
- Logs estruturados em formato JSON
- *Health checks* através de *liveness probes* e *readiness probes*
- Execução manual da DAG através de `schedule=None`
- Idempotência do pipeline através de `ON CONFLICT DO UPDATE`

### O que foi deixado de fora

- Configuração distribuída do Airflow com múltiplos *workers*
- Publicação de imagens Docker em *registry* externo
- Deploy automático para Kubernetes
- Integração direta entre a aplicação FastAPI e o PostgreSQL
- Execução de testes unitários e de integração
- Análise estática de código e verificações de segurança
- Observabilidade avançada com Prometheus e Grafana
- Gestão de segredos através de ferramentas dedicadas
- Versionamento automático de imagens Docker

### Motivações

As decisões adotadas tiveram como objetivo garantir que a solução fosse:

- Simples
- Reproduzível
- Modular
- Fácil de demonstrar
- Fácil de evoluir
- Próxima de uma arquitetura de produção
- Alinhada com o escopo do desafio técnico

A separação entre o ambiente de dados, a aplicação executada em Kubernetes e o pipeline de CI/CD reduz o acoplamento entre componentes e facilita a manutenção e evolução futura da solução.

As credenciais definidas no projeto destinam-se exclusivamente a fins demonstrativos e ao ambiente local de desenvolvimento.