# SIAC Authorization Server - Dockerfile
# Microservicio minimalista para OAuth 2.1

# Stage 1: Build stage para dependencias
FROM python:3.11-slim as builder

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

# Instalar dependencias runtime
RUN apt-get update && apt-get install -y \
    libssl3 \
    libffi8 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r auth && useradd -r -g auth auth

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias Python del stage builder
COPY --from=builder /root/.local /home/auth/.local

# Copiar código de la aplicación
COPY main.py .

# Crear directorio para logs
RUN mkdir -p /app/logs && chown -R auth:auth /app

# Cambiar al usuario no-root
USER auth

# Configurar PATH para incluir dependencias locales
ENV PATH=/home/auth/.local/bin:$PATH

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV AUTH_SERVER_ISSUER=https://auth.siac-app.com

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]



