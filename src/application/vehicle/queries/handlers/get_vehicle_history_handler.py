"""Vehicle query handlers."""

import logging
from typing import List
from src.application.shared.query_bus import QueryHandler
from src.application.vehicle.commands import GetVehicleHistoryQuery
from src.domain.vehicle.repositories import VehicleRepository

logger = logging.getLogger(__name__)


class GetVehicleHistoryHandler(QueryHandler[GetVehicleHistoryQuery, List[dict]]):
    """Handler for getting vehicle history queries."""
    
    def __init__(
        self,
        vehicle_repo: VehicleRepository,
        logger: logging.Logger
    ):
        self.vehicle_repo = vehicle_repo
        self.logger = logger
    
    async def handle(self, query: GetVehicleHistoryQuery) -> List[dict]:
        """Handle a vehicle history query."""
        try:
            vehicle = await self.vehicle_repo.find_by_id(query.vehicle_id)
            if not vehicle:
                return []
            
            # Convert decode history to serializable format
            history = []
            for attempt in vehicle.decode_history:
                history.append({
                    "timestamp": attempt.timestamp.isoformat(),
                    "service_used": attempt.service_used,
                    "success": attempt.success,
                    "error_message": attempt.error_message
                })
            
            return history
        except Exception as e:
            self.logger.error(f"Error handling get vehicle history query: {e}")
            raise