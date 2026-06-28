from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # database settings
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str
    
    # app
    app_env: str = "dev"
    log_level: str = "INFO"

    # binance
    binance_base_url: str
    binance_symbols: list[str]
    binance_limit: int = 1000

    model_config = {"env_file": ".env"}

    @property
    def database_url(self) -> str:
        return(
            f"postgresql+asyncpg://{self.postgres_user}"
            f":{self.postgres_password}"
            f"@{self.postgres_host}"
            f":{self.postgres_port}"
            f"/{self.postgres_db}"
        )
settings = Settings()  # type: ignore[call-arg]