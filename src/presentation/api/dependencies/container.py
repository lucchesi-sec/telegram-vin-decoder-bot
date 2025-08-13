"""Dependency injection for API layer."""

from fastapi import Depends
from src.config.dependencies import Container


def get_container() -> Container:
    """Get the dependency injection container."""
    return Container()


def get_vehicle_service(container: Container = Depends(get_container)):
    """Get the vehicle application service."""
    return container.vehicle_service()


def get_user_service(container: Container = Depends(get_container)):
    """Get the user application service."""
    return container.user_service()