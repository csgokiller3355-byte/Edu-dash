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

# Всегда работаем в корне /app, чтобы пути относительно него были предсказуемыми
WORKDIR /app

COPY . .

# Сборка статики через явный путь к manage.py
RUN python App/manage.py collectstatic --noinput

EXPOSE 8000

# Запуск Gunicorn с PYTHONPATH=. чтобы Python видел вложенный пакет App.App.wsgi
CMD ["sh", "-c", "PYTHONPATH=. gunicorn App.App.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]