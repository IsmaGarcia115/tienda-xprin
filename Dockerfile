# Imagen base de Python
FROM python:3.9-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la carpeta app
COPY app/ ./app/

# Exponer el puerto de Flask
EXPOSE 5000

# Variables de entorno
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para ejecutar Flask
CMD ["flask", "run"]