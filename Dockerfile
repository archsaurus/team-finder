FROM python:3.14-slim AS builder

RUN apt-get update && apt-get install -y \
    gcc curl postgresql-client libpq-dev fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .


FROM python:3.14-slim AS production

RUN apt-get update && apt-get install -y \
    libpq5 fonts-dejavu-core curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

RUN groupadd -r appuser && useradd -r -g appuser appuser && chown -R appuser:appuser /app

RUN mkdir -p /home/appuser && chown -R appuser:appuser /home/appuser
RUN mkdir -p /tmp/appuser && chown -R appuser:appuser /tmp/appuser

USER appuser


EXPOSE 8000

CMD sh -c "python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    python manage.py create_test_data --seed 42 && \
    exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-tmp-dir /tmp/appuser \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 120 \
    --preload \
    team_finder.wsgi:application"
