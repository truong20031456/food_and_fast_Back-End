"""
Auth Service FastAPI application factory
"""

from typing import List, Optional, Callable
from fastapi import FastAPI
import sys
import os

# Add path for shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from shared_code.core.app import create_app
from shared_code.core.config import BaseServiceSettings


def create_auth_app(
    settings: BaseServiceSettings,
    routers: Optional[List] = None,
    startup_tasks: Optional[List[Callable]] = None,
    shutdown_tasks: Optional[List[Callable]] = None,
) -> FastAPI:
    """
    Create Auth Service FastAPI application

    Args:
        settings: Service settings
        routers: List of router objects to include
        startup_tasks: List of startup tasks
        shutdown_tasks: List of shutdown tasks

    Returns:
        Configured FastAPI application
    """
    return create_app(
        service_name="Auth Service",
        settings=settings,
        routers=routers,
        startup_tasks=startup_tasks,
        shutdown_tasks=shutdown_tasks,
    )
