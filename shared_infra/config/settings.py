"""Global application configuration - DATABASE_URL, LOG_LEVEL, ENABLE_EMAIL_SERVICE"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field(..., env="DATABASE_URL")
    echo: bool = Field(default=False, env="DB_ECHO")
    pool_size: int = Field(default=5, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration"""
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    
    class Config:
        env_prefix = "REDIS_"


class EmailSettings(BaseSettings):
    """Email service configuration"""
    enabled: bool = Field(default=True, env="EMAIL_SERVICE_ENABLED")
    smtp_host: str = Field(default="localhost", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    from_email: Optional[str] = Field(default=None, env="FROM_EMAIL")
    
    class Config:
        env_prefix = "EMAIL_"


class SecuritySettings(BaseSettings):
    """Security configuration"""
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    
    @validator("secret_key", "jwt_secret_key")
    def validate_secret_keys(cls, v):
        if len(v) < 32:
            raise ValueError("Secret keys must be at least 32 characters long")
        return v
    
    class Config:
        env_prefix = "SECURITY_"


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_file_size: int = Field(default=10485760, env="LOG_MAX_FILE_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    @validator("level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    class Config:
        env_prefix = "LOG_"


class ApplicationSettings(BaseSettings):
    """Main application settings"""
    
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    
    # API settings
    title: str = Field(default="AM User Management API")
    description: str = Field(default="User management system with modular architecture")
    version: str = Field(default="0.1.0")
    
    # Database settings
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # Security
    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = ApplicationSettings()