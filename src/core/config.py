from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "llm-compare-app"
    database_url: str = "sqlite:///./app.db"

    # ローカルLLM
    local_llm_base_url: str = "http://host.docker.internal:9000"
    local_llm_timeout_sec: float = 120.0
    local_llm_model_name: str = "gemma"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """環境変数を反映した設定オブジェクトを生成する。"""
    return Settings()
