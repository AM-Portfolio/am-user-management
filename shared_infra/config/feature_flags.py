"""Feature flags configuration - Central toggle: ENABLE_ACCOUNT_MANAGEMENT=True"""
from typing import Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class FeatureFlags(BaseSettings):
    """Application feature flags"""
    
    # Module toggles
    enable_account_management: bool = Field(default=True, env="ENABLE_ACCOUNT_MANAGEMENT")
    enable_user_profile: bool = Field(default=True, env="ENABLE_USER_PROFILE")
    enable_subscription: bool = Field(default=True, env="ENABLE_SUBSCRIPTION")
    enable_permissions_roles: bool = Field(default=True, env="ENABLE_PERMISSIONS_ROLES")
    
    # Feature toggles
    enable_email_verification: bool = Field(default=True, env="ENABLE_EMAIL_VERIFICATION")
    enable_phone_verification: bool = Field(default=False, env="ENABLE_PHONE_VERIFICATION")
    enable_2fa: bool = Field(default=False, env="ENABLE_2FA")
    enable_password_reset: bool = Field(default=True, env="ENABLE_PASSWORD_RESET")
    enable_account_lockout: bool = Field(default=True, env="ENABLE_ACCOUNT_LOCKOUT")
    
    # API features
    enable_api_rate_limiting: bool = Field(default=True, env="ENABLE_API_RATE_LIMITING")
    enable_api_versioning: bool = Field(default=True, env="ENABLE_API_VERSIONING")
    enable_swagger_docs: bool = Field(default=True, env="ENABLE_SWAGGER_DOCS")
    
    # Infrastructure features
    enable_redis_caching: bool = Field(default=True, env="ENABLE_REDIS_CACHING")
    enable_event_publishing: bool = Field(default=True, env="ENABLE_EVENT_PUBLISHING")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_health_checks: bool = Field(default=True, env="ENABLE_HEALTH_CHECKS")
    
    # Development features
    enable_debug_logging: bool = Field(default=False, env="ENABLE_DEBUG_LOGGING")
    enable_mock_email: bool = Field(default=False, env="ENABLE_MOCK_EMAIL")
    enable_test_endpoints: bool = Field(default=False, env="ENABLE_TEST_ENDPOINTS")
    
    def get_enabled_modules(self) -> Dict[str, bool]:
        """Get dictionary of enabled modules"""
        return {
            "account_management": self.enable_account_management,
            "user_profile": self.enable_user_profile,
            "subscription": self.enable_subscription,
            "permissions_roles": self.enable_permissions_roles,
        }
    
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a specific module is enabled"""
        return self.get_enabled_modules().get(module_name, False)
    
    def get_all_flags(self) -> Dict[str, Any]:
        """Get all feature flags as dictionary"""
        return self.dict()
    
    class Config:
        env_prefix = "FEATURE_"
        case_sensitive = False


# Global feature flags instance
feature_flags = FeatureFlags()


def require_feature(feature_name: str):
    """Decorator to require a feature flag to be enabled"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not getattr(feature_flags, feature_name, False):
                raise RuntimeError(f"Feature '{feature_name}' is not enabled")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_module(module_name: str):
    """Decorator to require a module to be enabled"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not feature_flags.is_module_enabled(module_name):
                raise RuntimeError(f"Module '{module_name}' is not enabled")
            return func(*args, **kwargs)
        return wrapper
    return decorator