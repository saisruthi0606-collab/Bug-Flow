from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "BugFlow"
    database_url: str = "sqlite:///./bugflow.db"
    jwt_secret_key: str = "supersecretkey"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
