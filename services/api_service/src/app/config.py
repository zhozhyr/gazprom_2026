from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_host: str
    app_port: int
    database_url: str
    kafka_bootstrap_servers: str
    kafka_enabled: bool
    kafka_client_id: str
    kafka_topic_permit_submitted: str
    kafka_topic_permit_reviewed: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
