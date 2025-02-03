from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI 3-Layered Architecture"
    API_VERSION: str = "v1"

    class Config:
        env_file = ".env"

settings = Settings()
