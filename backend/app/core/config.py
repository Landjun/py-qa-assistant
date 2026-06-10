"""统一配置读取模块。

所有配置从环境变量 / .env 读取，禁止在代码中硬编码密钥。
通过 `from app.core.config import settings` 获取单例。
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 服务元信息
    service_name: str = "python-qa-customer-service"
    debug: bool = False

    # DeepSeek（Chat）
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # DashScope（Embedding / Rerank / Vision，复用同一 Key）
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_model: str = "text-embedding-v4"
    rerank_model: str = "qwen3-rerank"
    vision_model: str = "qwen-vl-max"

    # 存储
    database_url: str = "sqlite:///./data/app.db"
    faiss_index_path: str = "./data/faiss.index"

    # CORS：允许的前端来源，逗号分隔
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # JWT 认证
    jwt_secret_key: str = "dev-secret-please-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 天

    # 种子账号密码（从 .env 读取，不可硬编码）
    seed_admin_password: str = ""
    seed_test_password: str = ""
    seed_qa_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """带缓存的配置工厂，便于测试时覆盖。"""
    return Settings()


settings = get_settings()
