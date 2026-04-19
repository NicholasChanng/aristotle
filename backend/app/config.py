from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_ROOT / ".env", override=True)
load_dotenv(BACKEND_ROOT / ".env.local", override=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_ROOT / ".env"), str(BACKEND_ROOT / ".env.local")),
        extra="ignore",
    )

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    chroma_persist_dir: str = "./chroma_data"
    database_url: str = "sqlite:///./app.db"
    demo_course_dir: str = "../demo_course"
    lecture_json_dir: str = "../cs188/lectures"

    cors_origins: str = "http://localhost:3000"
    jwt_secret: str = "dev-only-not-used-in-mvp"
    app_env: str = "development"

    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_vision_model: str = "claude-haiku-4-5"
    embedding_model: str = "text-embedding-3-small"
    whisper_model: str = "whisper-1"

    retrieval_timeout_s: float = 5.0
    generation_timeout_s: float = 90.0
    retrieval_k: int = 8
    max_context_chars: int = 7000
    max_context_chunk_chars: int = 1000

    def _resolve_project_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path
        backend_root = Path(__file__).resolve().parents[1]
        return (backend_root / path).resolve()

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def demo_course_path(self) -> Path:
        return self._resolve_project_path(self.demo_course_dir)

    @property
    def lecture_json_path(self) -> Path:
        return self._resolve_project_path(self.lecture_json_dir)


settings = Settings()
