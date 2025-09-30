"""Structured JSON logger configuration"""
import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime
from logging.handlers import RotatingFileHandler

from ..config.settings import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname", 
                "filename", "module", "lineno", "funcName", "created", 
                "msecs", "relativeCreated", "thread", "threadName", 
                "processName", "process", "message", "exc_info", "exc_text", 
                "stack_info"
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records"""
    
    def __init__(self, context: Dict[str, Any] = None):
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record"""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def setup_logging() -> None:
    """Setup application logging configuration"""
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.logging.level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    if settings.logging.format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if configured
    if settings.logging.file_path:
        file_handler = RotatingFileHandler(
            settings.logging.file_path,
            maxBytes=settings.logging.max_file_size,
            backupCount=settings.logging.backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for external libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.database.echo else logging.WARNING
    )


def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance with optional name"""
    return logging.getLogger(name or __name__)


def add_context_to_logger(logger: logging.Logger, **context) -> None:
    """Add context filter to logger"""
    context_filter = ContextFilter(context)
    logger.addFilter(context_filter)


# Application logger instance
logger = get_logger("am-user-management")


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log info message with context"""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message with context"""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message with context"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug message with context"""
        self.logger.debug(message, extra=kwargs)