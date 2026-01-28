from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "ITSM Asset Management API"
    DEBUG: bool = False
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    COLLECT_API_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
