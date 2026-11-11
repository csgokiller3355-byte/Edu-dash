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

# Сначала копируем проект в общий корень /app
WORKDIR /app
COPY . .

# Переходим в рабочую директорию внутрь папки App, где лежит manage.py
WORKDIR /app/App

# Собираем статику
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Запускаем Gunicorn (теперь путь App.wsgi корректно найдет настройки App.settings)
CMD ["sh", "-c", "gunicorn App.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]