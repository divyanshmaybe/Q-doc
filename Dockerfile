FROM python:3.12-slim

WORKDIR /app

# Headless OpenCV does not need desktop OpenGL libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-render.txt .
RUN python -m pip install --no-cache-dir -r requirements-render.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "exec python -m uvicorn services.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

