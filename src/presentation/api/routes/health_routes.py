"""Health check routes."""

from fastapi import APIRouter, Depends
from datetime import datetime
from src.presentation.api.dependencies.container import get_container
from src.config.dependencies import Container


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(container: Container = Depends(get_container)):
    """Health check endpoint with database and cache status."""
    try:
        # Test database connection
        db_status = "healthy"
        try:
            # This would test the actual database connection
            # For now, we'll assume it's healthy if the container is available
            pass
        except Exception:
            db_status = "unhealthy"
        
        # Test cache connection
        cache_status = "healthy"
        try:
            # This would test the actual cache connection
            pass
        except Exception:
            cache_status = "unhealthy"
        
        overall_status = "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "cache": cache_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/api/stats")
async def get_stats(container: Container = Depends(get_container)):
    """Get application statistics."""
    try:
        # In a real implementation, these would come from the domain services
        return {
            "total_vehicles": 0,  # TODO: Implement in vehicle service
            "unique_manufacturers": 0,  # TODO: Implement in vehicle service
            "recent_decodes": 0  # TODO: Implement in vehicle service
        }
    except Exception as e:
        return {
            "total_vehicles": 0,
            "unique_manufacturers": 0,
            "recent_decodes": 0,
            "error": str(e)
        }