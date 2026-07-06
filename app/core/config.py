from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Teacher"
    app_env: str = "development"
    app_debug: bool = True
    app_secret_key: str = "change-me"

    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    vector_store_type: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"

    database_url: str = "sqlite:///./data/ai_teacher.db"

    voice_sample_rate: int = 16000
    enable_voice: bool = True

    uploads_dir: str = "./data/uploads"
    documents_json: str = "./data/documents.json"

    class Config:
        env_file = ".env"


settings = Settings()