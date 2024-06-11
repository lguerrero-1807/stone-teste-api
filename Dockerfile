# Usar uma imagem base oficial do Python
FROM python:3.9-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os requisitos para o diretório de trabalho
COPY app/requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação para o diretório de trabalho
COPY app/app.py .

# Expor a porta na qual a aplicação será executada
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app.py"]
