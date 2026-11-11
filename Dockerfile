# ---------------------
# Build stage
# ---------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------
# Production stage
# ---------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

# Базовая рабочая директория
WORKDIR /app

# Копируем всё содержимое репозитория в /app
COPY . .

# Собираем статику, указывая путь через папку App
RUN python App/manage.py collectstatic --noinput

EXPOSE 8000

# Запускаем Gunicorn, используя PYTHONPATH для корректного импорта вложенного пакета
CMD ["sh", "-c", "PYTHONPATH=. gunicorn App.App.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]