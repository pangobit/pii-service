from gliner import GLiNER

from app.config import Settings


class ModelNotLoadedError(RuntimeError):
    pass


_model: GLiNER | None = None


def load_model(settings: Settings) -> GLiNER:
    global _model
    _model = GLiNER.from_pretrained(
        settings.model_dir,
        load_onnx_model=True,
        onnx_model_file=settings.onnx_model_file,
        map_location="cpu",
    )
    return _model


def get_model() -> GLiNER:
    if _model is None:
        raise ModelNotLoadedError("model not loaded")
    return _model


def predict(
    text: str,
    labels: list[str],
    threshold: float,
) -> list[dict]:
    entities = get_model().predict_entities(
        text,
        labels,
        threshold=threshold,
    )
    return [
        {
            "text": entity["text"],
            "label": entity["label"],
            "start": entity["start"],
            "end": entity["end"],
            "score": float(entity["score"]),
        }
        for entity in entities
    ]