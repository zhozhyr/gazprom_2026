from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Permit API Service"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite+aiosqlite:///./permit_api.db"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_enabled: bool = False
    kafka_client_id: str = "permit-api-service"
    kafka_topic_permit_submitted: str = "permits.submitted"
    kafka_topic_permit_reviewed: str = "permits.reviewed"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
