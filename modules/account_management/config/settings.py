"""Account management module configuration"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class AccountManagementSettings(BaseSettings):
    """Account management configuration settings"""
    
    # Password settings
    password_min_length: int = Field(default=8, ge=6, le=128)
    password_max_length: int = Field(default=128)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_numbers: bool = Field(default=True)
    password_require_special: bool = Field(default=True)
    
    # Email verification settings
    email_verification_enabled: bool = Field(default=True)
    email_verification_token_expiry_hours: int = Field(default=24)
    
    # Account security settings
    max_login_attempts: int = Field(default=5)
    account_lockout_minutes: int = Field(default=15)
    
    # Password reset settings
    password_reset_token_expiry_hours: int = Field(default=1)
    
    # Registration settings
    allow_registration: bool = Field(default=True)
    require_phone_verification: bool = Field(default=False)
    
    class Config:
        env_prefix = "ACCOUNT_MGMT_"
        case_sensitive = False


# Global instance
account_settings = AccountManagementSettings()