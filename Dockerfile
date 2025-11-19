# Imagen ligera y compatible con wheels precompiladas
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema (mínimas). Amplía si alguna lib hace falta.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar el cache de Docker
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Variables de entorno
ENV HOST=0.0.0.0 \
    PORT=8000

EXPOSE 8000

# Comando por defecto: levantar API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]


