# Usar a imagem do Python 3.9
FROM python:3.9-slim

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos de requirements
COPY requirements.txt requirements.txt

# Instalar as dependências
RUN pip install -r requirements.txt

# Copiar o código-fonte do Django para o container
COPY . .

# Expor a porta 8000 para o servidor web do Django
EXPOSE 8000

# Comando padrão (será sobrescrito no docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:3344"]
