# SIAC Assistant - Dockerfile para Producción
# Multi-stage build para optimizar el tamaño de la imagen

# Stage 1: Build stage para dependencias
FROM python:3.11-slim as builder

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY server/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

# Instalar dependencias runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r siac && useradd -r -g siac siac

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias Python del stage builder
COPY --from=builder /root/.local /home/siac/.local

# Copiar código de la aplicación
COPY server/ ./server/
COPY web/dist/ ./web/dist/

# Crear directorio para logs
RUN mkdir -p /app/logs && chown -R siac:siac /app

# Cambiar al usuario no-root
USER siac

# Configurar PATH para incluir dependencias locales
ENV PATH=/home/siac/.local/bin:$PATH

# Variables de entorno
ENV PYTHONPATH=/app/server
ENV PYTHONUNBUFFERED=1
ENV BASE_URL=https://api.siac-app.com

# Exponer puerto
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/health || exit 1

# Comando de inicio
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8888", "--workers", "1"]



