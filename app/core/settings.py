from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # database settings
    database_url: str
    postgres_host: str
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

settings = Settings()  # type: ignore[call-arg]