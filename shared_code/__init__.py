"""
Shared Code Module for Food Fast E-commerce Platform

This module provides common components, utilities, and services
that are shared across all microservices in the platform.

Main Components:
    - cache: Redis-based caching system
    - core: Core configuration and base classes  
    - middleware: Common middleware components
    - monitoring: Performance monitoring and observability
    - models: Shared data models
    - services: Shared business services
    - utils: Common utility functions

Quick Start:
    # Import cache service
    from shared_code.cache import get_cache_service
    
    # Import base configuration
    from shared_code.core.config import BaseSettings
    
    # Import logging utilities
    from shared_code.utils.logging import get_logger

Version: 1.0.0
Author: Food Fast Development Team
"""

# Version information
__version__ = "1.0.0"
__author__ = "Food Fast Development Team"

# Main exports
from .cache import get_cache_service
from .core.config import BaseSettings
from .utils.logging import get_logger

__all__ = [
    'get_cache_service',
    'BaseSettings', 
    'get_logger',
    '__version__',
    '__author__'
]