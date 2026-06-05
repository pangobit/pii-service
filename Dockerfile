FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_DIR=/app/model \
    ONNX_MODEL_FILE=onnx/model_quint8.onnx \
    DEFAULT_THRESHOLD=0.3 \
    HF_HOME=/tmp/hf-cache

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN hf download knowledgator/gliner-pii-base-v1.0 \
    --local-dir /app/model \
    --exclude "pytorch_model.bin" \
    --exclude "trainer_state.json" \
    --exclude "onnx/model.onnx" \
    --exclude "onnx/model_fp16.onnx"

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]