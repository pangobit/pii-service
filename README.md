# PII Service

A small HTTP API that finds personally identifiable information (PII) in text. It runs locally in Docker and uses the [Knowledgator GLiNER PII model](https://huggingface.co/knowledgator/gliner-pii-base-v1.0) with a compact ONNX build (CPU, no cloud API calls).

You send plain text and a list of entity types to look for (or use the built-in defaults). The service returns each match with its label, position in the string, and confidence score.

## Quick start

**Requirements:** Docker and Docker Compose.

```bash
git clone git@github.com:pangobit/pii-service.git
cd pii-service
docker compose up --build
```

The first build downloads the model into the image; it can take several minutes. When the container is healthy, the API is at [http://localhost:8000](http://localhost:8000).

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Try it

**Health check**

```bash
curl http://localhost:8000/health
```

**Detect PII (default label set)**

```bash
curl -s -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "John Smith called from 415-555-1234 about account 12345678."}'
```

**Detect specific types only**

```bash
curl -s -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "John Smith called from 415-555-1234.",
    "labels": ["name", "phone number"],
    "threshold": 0.3
  }'
```

Example response:

```json
{
  "entities": [
    {
      "text": "John Smith",
      "label": "name",
      "start": 0,
      "end": 10,
      "score": 0.97
    },
    {
      "text": "415-555-1234",
      "label": "phone number",
      "start": 23,
      "end": 35,
      "score": 0.97
    }
  ]
}
```

**List default labels**

```bash
curl http://localhost:8000/labels
```

## API summary

| Method | Path       | Description                                      |
|--------|------------|--------------------------------------------------|
| GET    | `/health`  | Service is up and the model is loaded            |
| GET    | `/labels`  | Default PII entity types used when `labels` omitted |
| POST   | `/predict` | Run detection on one string                      |

**POST `/predict` body**

| Field       | Required | Description |
|-------------|----------|-------------|
| `text`      | yes      | Input string to scan |
| `labels`    | no       | Entity types to search for; omit to use the default preset |
| `threshold` | no       | Minimum confidence (0–1); default `0.3` |

GLiNER is zero-shot: you can pass custom label strings (for example `"policy number"`) even if they are not in the default list.

## Pre-built image (GHCR)

Released images are published to GitHub Container Registry when a semver tag is pushed (for example `v1.0.0`).

```bash
docker pull ghcr.io/pangobit/pii-service:1.0.0
docker run --rm -p 8000:8000 ghcr.io/pangobit/pii-service:1.0.0
```

Replace `1.0.0` with the version you need. Tags follow the git tag without the `v` prefix (`v1.0.0` → `1.0.0`).

## Configuration

Environment variables (also set in `docker-compose.yml`):

| Variable            | Default                      | Meaning |
|---------------------|------------------------------|---------|
| `MODEL_DIR`         | `/app/model`                 | Path to the model files inside the container |
| `ONNX_MODEL_FILE`   | `onnx/model_quint8.onnx`     | ONNX weights file (relative to `MODEL_DIR`) |
| `DEFAULT_THRESHOLD` | `0.3`                        | Default confidence cutoff for `/predict` |

## How it works (short version)

1. Text and labels are tokenized and scored by a GLiNER NER model.
2. Spans above the threshold are returned as entities.
3. Inference uses ONNX Runtime on CPU; the quantized model keeps memory and image size reasonable compared to full PyTorch weights.

The model is baked into the Docker image at build time, so production containers do not call Hugging Face on startup.

## License and model

Application code in this repository is licensed under the [Apache License 2.0](LICENSE).

The baked-in weights come from [knowledgator/gliner-pii-base-v1.0](https://huggingface.co/knowledgator/gliner-pii-base-v1.0), which is also Apache-2.0 on Hugging Face. Docker images that include the model should preserve upstream license notices when you redistribute them.