from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import Settings
from app.inference import ModelNotLoadedError, load_model, predict
from app.labels import DEFAULT_PII_LABELS

settings = Settings()


class PredictRequest(BaseModel):
    text: str = Field(min_length=1)
    labels: list[str] | None = None
    threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class Entity(BaseModel):
    text: str
    label: str
    start: int
    end: int
    score: float


class PredictResponse(BaseModel):
    entities: list[Entity]


class LabelsResponse(BaseModel):
    labels: list[str]


class HealthResponse(BaseModel):
    status: str
    model_dir: str
    onnx_model_file: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    load_model(settings)
    yield


app = FastAPI(title="PII Service", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        from app.inference import get_model

        get_model()
    except ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return HealthResponse(
        status="ok",
        model_dir=settings.model_dir,
        onnx_model_file=settings.onnx_model_file,
    )


@app.get("/labels", response_model=LabelsResponse)
def labels() -> LabelsResponse:
    return LabelsResponse(labels=list(DEFAULT_PII_LABELS))


@app.post("/predict", response_model=PredictResponse)
def predict_entities(body: PredictRequest) -> PredictResponse:
    label_list = body.labels if body.labels else list(DEFAULT_PII_LABELS)
    if not label_list:
        raise HTTPException(status_code=400, detail="labels must not be empty")
    threshold = (
        body.threshold if body.threshold is not None else settings.default_threshold
    )
    try:
        entities = predict(body.text, label_list, threshold)
    except ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return PredictResponse(entities=[Entity(**entity) for entity in entities])