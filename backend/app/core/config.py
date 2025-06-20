# backend/app/core/config.py
from typing import List, Optional, Union, Any
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CyberEd Pro"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-for-jwt-here"  # Change this in production!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database connection
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "cybered_admin"
    POSTGRES_PASSWORD: str = "cyber_secure_pwd"
    POSTGRES_DB: str = "cybered_pro"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode='before')
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v

        # Since we're not directly using the build method, let's create the URL string
        # and then parse it with PostgresDsn
        postgres_user = info.data.get("POSTGRES_USER", "")
        postgres_password = info.data.get("POSTGRES_PASSWORD", "")
        postgres_server = info.data.get("POSTGRES_SERVER", "")
        postgres_port = info.data.get("POSTGRES_PORT", "5432")
        postgres_db = info.data.get("POSTGRES_DB", "")

        # Build the connection string manually
        connection_str = f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:{postgres_port}/{postgres_db}"
        return connection_str

    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

# Create settings instance
settings = Settings()