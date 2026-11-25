from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Sudarsan Portfolio API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    frontend_origin: str = "http://localhost:5500"

    database_url: str = "sqlite:///./portofolio.db"

    # JWT security settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    # Jwt Security Settings (refresh token)
    refresh_token_secret_key: str
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()