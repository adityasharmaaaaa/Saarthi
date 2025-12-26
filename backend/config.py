import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str
    
    # Paths (Dynamically calculated based on file location)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    CHROMA_PATH: str = os.path.join(DATA_DIR, "chroma_db")
    
    # Model Configs
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    RERANKING_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"

# Initialize settings
settings = Settings()