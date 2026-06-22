# Imagem base leve com Python 3.12
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o ficheiro de dependências para dentro da imagem
COPY requirements.txt .

# Instala as dependências da aplicação
# --no-cache-dir evita guardar cache do pip, deixando a imagem menor
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação para dentro da imagem
COPY main.py .

# Documenta que a aplicação escuta na porta 8000
EXPOSE 8000

# Comando executado quando o container inicia
# Uvicorn sobe a aplicação FastAPI definida em main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]