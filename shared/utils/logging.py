"""
Centralized logging configuration
"""
import logging
import sys
from typing import Optional
from datetime import datetime
import json
from pathlib import Path

from ..core.config import BaseServiceSettings, LogLevel


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
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
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created",
                "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "exc_info", "exc_text", "stack_info"
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ServiceLogger:
    """Service-specific logger configuration"""
    
    def __init__(self, service_name: str, settings: BaseServiceSettings):
        self.service_name = service_name
        self.settings = settings
        self.logger = logging.getLogger(service_name)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        level = getattr(logging, self.settings.LOG_LEVEL.value)
        self.logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Use JSON formatter in production, simple formatter in development
        if self.settings.is_production:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        if hasattr(self.settings, 'LOG_FILE') and self.settings.LOG_FILE:
            log_file = Path(self.settings.LOG_FILE)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
        
        self.logger.info(f"Logging configured for {self.service_name}")
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get logger instance"""
        if name:
            return logging.getLogger(f"{self.service_name}.{name}")
        return self.logger


def setup_logging(service_name: str, settings: BaseServiceSettings) -> ServiceLogger:
    """Setup logging for a service"""
    return ServiceLogger(service_name, settings)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)


# Context manager for request logging
class RequestLogger:
    """Context manager for request-specific logging"""
    
    def __init__(self, logger: logging.Logger, request_id: str, method: str, path: str):
        self.logger = logger
        self.request_id = request_id
        self.method = method
        self.path = path
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(
            "Request started",
            extra={
                "request_id": self.request_id,
                "method": self.method,
                "path": self.path,
                "start_time": self.start_time.isoformat()
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        log_data = {
            "request_id": self.request_id,
            "method": self.method,
            "path": self.path,
            "duration": duration,
            "end_time": end_time.isoformat()
        }
        
        if exc_type:
            self.logger.error(
                f"Request failed: {exc_val}",
                extra=log_data,
                exc_info=True
            )
        else:
            self.logger.info(
                "Request completed",
                extra=log_data
            )


def log_request(logger: logging.Logger, request_id: str, method: str, path: str):
    """Create request logger context manager"""
    return RequestLogger(logger, request_id, method, path)