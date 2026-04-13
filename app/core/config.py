from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Regulatory Workflow Automation API"
    version: str = "1.0.0"
    max_summary_chunk_chars: int = 1800
    duplicate_similarity_threshold: float = 0.84
    pseudonym_seed: int = 42


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
