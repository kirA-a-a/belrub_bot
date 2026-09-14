FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Railway may inject secrets at build but not runtime — bake token file at build.
ARG TELEGRAM_TOKEN=
ARG BOT_TOKEN=
ARG TELEGRAM_BOT_TOKEN=

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x /app/entrypoint.sh \
    && mkdir -p /app/data \
    && TOKEN="${TELEGRAM_TOKEN:-${TELEGRAM_BOT_TOKEN:-${BOT_TOKEN:-}}}" \
    && if [ -n "$TOKEN" ]; then printf '%s' "$TOKEN" > /app/data/telegram_token; fi \
    && if [ -f /app/data/telegram_token ]; then echo "build: telegram_token file written"; else echo "build: telegram_token missing (set TELEGRAM_TOKEN for Build)"; fi

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "print('ok')"

CMD ["/app/entrypoint.sh"]
