#!/usr/bin/env python3
import os
import sys
import time

from huggingface_hub import snapshot_download

REPO_ID = "knowledgator/gliner-pii-base-v1.0"
LOCAL_DIR = os.environ.get("MODEL_DOWNLOAD_DIR", "/app/model")
MAX_ATTEMPTS = int(os.environ.get("HF_DOWNLOAD_ATTEMPTS", "6"))
ALLOW_PATTERNS = [
    "onnx/model_quint8.onnx",
    "gliner_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "spm.model",
    "added_tokens.json",
    "special_tokens_map.json",
]


def main() -> None:
    token = os.environ.get("HF_TOKEN") or None
    if token:
        print("Using HF_TOKEN for authenticated download.", file=sys.stderr)
    else:
        print(
            "No HF_TOKEN set; download may be rate-limited on CI.",
            file=sys.stderr,
        )

    last_error: BaseException | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            path = snapshot_download(
                repo_id=REPO_ID,
                local_dir=LOCAL_DIR,
                allow_patterns=ALLOW_PATTERNS,
                token=token,
            )
            print(f"Model files ready at {path}", file=sys.stderr)
            return
        except Exception as exc:
            last_error = exc
            if attempt >= MAX_ATTEMPTS:
                break
            delay = min(60, 5 * (2 ** (attempt - 1)))
            print(
                f"Download attempt {attempt} failed ({exc!r}); "
                f"retrying in {delay}s...",
                file=sys.stderr,
            )
            time.sleep(delay)

    assert last_error is not None
    raise last_error


if __name__ == "__main__":
    main()