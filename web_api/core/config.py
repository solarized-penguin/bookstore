from datetime import timedelta
from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, Field
from pydantic.config import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False, env_file=(".env.debug", ".env.dev"), env_file_encoding="utf-8", extra="ignore"
    )


class RouterModelsDefaultConfigSettings(BaseConfig, env_prefix="BOOKS_ROUTER_MODELS_DEFAULTS_"):
    str_strip_whitespace: bool
    extra: Literal["allow", "ignore", "forbid"]
    use_enum_values: bool
    hide_input_in_errors: bool
    cache_strings: Literal["all", "keys", "none"]

    @property
    def config(self) -> ConfigDict:
        return ConfigDict(
            str_strip_whitespace=self.str_strip_whitespace,
            extra=self.extra,
            use_enum_values=self.use_enum_values,
            hide_input_in_errors=self.hide_input_in_errors,
            cache_strings=self.cache_strings,
        )


class LoggingSettings(BaseConfig, env_prefix="BOOKS_LOGGING_"):
    loki_endpoint: str
    loki_handler_version: str

    log_level: str
    log_format: str


class SecuritySettings(BaseConfig, env_prefix="BOOKS_SECURITY_"):
    bcrypt_truncate_error: bool
    user_password_regex: str
    user_incorrect_password_message: str
    user_password_encoding: str
    username_min_length: int
    username_max_length: int

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_token_expire_minutes: int = Field(
        ..., repr=False, exclude=True, description="Use 'jwt_token_default_expire_timedelta' property instead"
    )

    @property
    def jwt_token_default_expire_timedelta(self) -> timedelta:
        return timedelta(minutes=self.jwt_token_expire_minutes)


class ApiSettings(BaseConfig, env_prefix="BOOKS_API_"):
    title: str
    version: str
    host: str
    port: int
    debug: bool
    openapi_url: str
    docs_url: str
    redoc_url: str
    swagger_ui_oauth2_redirect_url: str
    include_in_schema: bool


class DbSettings(BaseConfig, env_prefix="BOOKS_DB_"):
    scheme: str
    name: str
    user: str
    password: str
    host: str
    port: int
    echo: bool
    pool_size: int

    @property
    def postgres_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.scheme,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.name,
        )


class Settings(BaseConfig):
    api: ApiSettings = ApiSettings()
    db: DbSettings = DbSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()
    router_models_config: RouterModelsDefaultConfigSettings = RouterModelsDefaultConfigSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
