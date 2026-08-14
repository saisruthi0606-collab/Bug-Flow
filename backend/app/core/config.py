from pathlib import Path
from pydantic_settings import BaseSettings

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    app_name: str = "BugFlow"
    database_url: str = f"sqlite:///{(ROOT_DIRECTORY / 'bugflow.db').as_posix()}"
    jwt_secret_key: str = "supersecretkey"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    upload_dir: str = str(ROOT_DIRECTORY / "uploads")
    class Config: env_file = ".env"
settings = Settings()
