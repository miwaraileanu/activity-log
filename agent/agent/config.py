import socket
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    API_URL: str = "http://localhost:8000"
    DEVICE_NAME: str = socket.gethostname()
    POLL_INTERVAL: float = 5.0
    BATCH_SIZE: int = 50
    WATCHED_DIRS: list[str] = []
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = AgentSettings()
