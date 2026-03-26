"""Scheduler: assigns sorted DeliveryRequests to vehicles."""
from __future__ import annotations

import logging

from logistics.models import Assignment, DeliveryRequest, DispatchPlan, Vehicle

logger = logging.getLogger(__name__)


class Scheduler:
    def dispatch(
        self,
        sorted_requests: list[DeliveryRequest],
        vehicles: list[Vehicle],
    ) -> DispatchPlan:
        """Assign requests to vehicles in sorted order.

        Iterates sorted_requests in order and assigns each to the first vehicle
        whose remaining_capacity_kg >= request.weight_kg. Decrements the
        vehicle's remaining_capacity_kg on assignment. Requests that fit no
        vehicle are deferred and logged.

        Returns a DispatchPlan with all assignments and deferred request IDs.
        """
        assignments: list[Assignment] = []
        deferred_request_ids: list[str] = []

        for request in sorted_requests:
            assigned = False
            for vehicle in vehicles:
                if vehicle.remaining_capacity_kg >= request.weight_kg:
                    vehicle.remaining_capacity_kg -= request.weight_kg
                    assignments.append(Assignment(vehicle_id=vehicle.id, request_id=request.id))
                    assigned = True
                    break

            if not assigned:
                reason = (
                    f"No vehicle has sufficient remaining capacity for request "
                    f"{request.id!r} (weight={request.weight_kg} kg). Deferring to next cycle."
                )
                logger.warning(reason)
                deferred_request_ids.append(request.id)

        return DispatchPlan(assignments=assignments, deferred_request_ids=deferred_request_ids)
