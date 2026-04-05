from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TabSense"
    DEBUG: bool = False

    # Database
    DB_PATH: str = str(Path(__file__).resolve().parent.parent / "tabsense.db")

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Inactivity defaults (in seconds)
    DEFAULT_INACTIVITY_THRESHOLD: int = 1800  # 30 minutes

    # CORS — allow Electron renderer and local extension
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
