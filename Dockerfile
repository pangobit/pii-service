FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/model \
    ONNX_MODEL_FILE=onnx/model_quint8.onnx \
    DEFAULT_THRESHOLD=0.3

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu \
    && ! pip list | grep -iE '^(nvidia|cuda-toolkit|triton)' \
    && find /usr/local/lib/python3.12/site-packages -type d -name __pycache__ -exec rm -rf {} + \
    && find /usr/local/lib/python3.12/site-packages -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete \
    && find /usr/local/lib/python3.12/site-packages -type d -name tests -exec rm -rf {} + \
    && find /usr/local/lib/python3.12/site-packages -type d -name test -exec rm -rf {} + \
    && find /usr/local/lib/python3.12/site-packages -type d \( -name benchmarks -o -name benchmark \) -exec rm -rf {} + \
    && rm -rf /usr/local/lib/python3.12/site-packages/torch/test

COPY model/ /app/model/
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]