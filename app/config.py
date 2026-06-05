from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    model_dir: str = "/app/model"
    onnx_model_file: str = "onnx/model_quint8.onnx"
    default_threshold: float = 0.3
    host: str = "0.0.0.0"
    port: int = 8000