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

# Устанавливаем рабочей директорией папку App, где лежит manage.py
WORKDIR /app/App

# Копируем содержимое корня проекта внутрь /app/App
COPY . /app/App

# Собираем статику из текущей директории
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Запускаем Gunicorn (так как мы находимся в /app/App, путь к wsgi: App.wsgi:application)
CMD ["sh", "-c", "gunicorn App.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]