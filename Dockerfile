# Usa Python 3.11 como imagen base
FROM python:3.11-slim

# Establece variables de entorno
# Previene que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Previene que Python almacene en buffer stdout y stderr
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema forzando IPv4 para evitar cuelgues de red
RUN apt-get -o Acquire::ForceIPv4=true update && \
    apt-get -o Acquire::ForceIPv4=true install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requisitos
COPY requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia el código del proyecto
COPY . /app/

# Expone el puerto 8000 (puerto por defecto de Django)
EXPOSE 8000

# Comando por defecto para ejecutar el servidor de desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]