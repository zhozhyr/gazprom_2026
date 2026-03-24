from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    kafka_bootstrap_servers: str
    kafka_client_id: str
    kafka_group_id: str
    kafka_topic_permit_submitted: str
    kafka_topic_compliance_passed: str
    kafka_topic_compliance_failed: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore[call-arg]
