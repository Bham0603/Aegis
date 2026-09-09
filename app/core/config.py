from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Aegis Security Gateway"
    ENVIRONMENT: str | None = None
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_STR: str = "/api/v1"

    # Security
    CORS_ORIGINS: list[str] = ["*"]
    MAX_BODY_SIZE: int = 10485760  # 10MB
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MIN: int = 120

    # Postgres
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "aegis"

    REDIS_URL: str = "redis://localhost:6379/0"
    POSTGRES_PORT: str = "5432"

    # AI Security Intelligence
    AI_SECURITY_ENABLED: bool = False
    AI_SECURITY_PROVIDER: str = "mock"
    AI_SECURITY_MODEL: str = "mock-model-v1"
    AI_SECURITY_BASE_URL: str | None = None
    AI_SECURITY_API_KEY: str | None = None
    AI_SECURITY_TIMEOUT: float = 5.0
    AI_SECURITY_MAX_INPUT_SIZE: int = 10240
    AI_SECURITY_MAX_OUTPUT_TOKENS: int = 1024

    @model_validator(mode="before")
    @classmethod
    def setup_env_and_cors(cls, data: dict) -> dict:
        # Map ENVIRONMENT to APP_ENV if present
        if "ENVIRONMENT" in data:
            data["APP_ENV"] = data["ENVIRONMENT"]

        # If production, make CORS strict by default if not overridden
        env = data.get("APP_ENV", "development")
        if env == "production" and "CORS_ORIGINS" not in data:
            data["CORS_ORIGINS"] = []
        return data

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.POSTGRES_SERVER == "sqlite":
            return f"sqlite+aiosqlite:///{self.POSTGRES_DB}"
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()
