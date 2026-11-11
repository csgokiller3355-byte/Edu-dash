# ---------------------
# Build stage
# ---------------------
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------
# Production stage
# ---------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Collect static files (указываем путь к manage.py с учетом папки App)
RUN python App/manage.py collectstatic --noinput

# Expose port (Render will override PORT at runtime)
EXPOSE 8000

# Run Gunicorn, добавляем PYTHONPATH=. чтобы Python корректно видел вложенный пакет App.App.wsgi
CMD ["sh", "-c", "PYTHONPATH=. gunicorn App.App.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]