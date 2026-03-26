"""Main entry point for the Logistics Network Optimizer — Module 1.

Wires PrioritizationEngine, Scheduler, and DispatchPlan together into a
single callable pipeline.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from logistics.engine import PrioritizationEngine
from logistics.models import DispatchPlan, SortMode, Vehicle
from logistics.scheduler import Scheduler


def main(raw_requests: list[dict], vehicles: list[Vehicle]) -> DispatchPlan:
    """Run the full prioritization and scheduling pipeline.

    1. Submits each raw request dict through PrioritizationEngine (validates
       and stores).
    2. Retrieves all accepted requests sorted by deadline (SortMode.DEADLINE).
    3. Passes the sorted list to Scheduler.dispatch for vehicle assignment.
    4. Prints and returns the resulting DispatchPlan.

    Args:
        raw_requests: List of raw delivery request dicts. Each must contain
                      weight_kg, deadline, customer_priority, and distance_km.
        vehicles:     List of Vehicle objects available for assignment.

    Returns:
        A DispatchPlan with assignments and any deferred request IDs.
    """
    engine = PrioritizationEngine()

    for raw in raw_requests:
        try:
            engine.submit(raw)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Rejected request {raw!r}: {exc}")

    sorted_requests = engine.get_sorted(SortMode.DEADLINE)
    scheduler = Scheduler()
    plan = scheduler.dispatch(sorted_requests, vehicles)

    print("=== Dispatch Plan ===")
    for assignment in plan.assignments:
        print(f"  Vehicle {assignment.vehicle_id!r} <- Request {assignment.request_id!r}")
    if plan.deferred_request_ids:
        print(f"  Deferred: {plan.deferred_request_ids}")
    else:
        print("  No deferred requests.")

    return plan


if __name__ == "__main__":
    now = datetime.utcnow()

    demo_requests = [
        {
            "weight_kg": 5.0,
            "deadline": now + timedelta(hours=3),
            "customer_priority": 2,
            "distance_km": 12.5,
        },
        {
            "weight_kg": 8.0,
            "deadline": now + timedelta(hours=1),
            "customer_priority": 1,
            "distance_km": 7.0,
        },
        {
            "weight_kg": 3.0,
            "deadline": now + timedelta(hours=2),
            "customer_priority": 3,
            "distance_km": 20.0,
        },
    ]

    demo_vehicles = [
        Vehicle(id="truck-1", capacity_kg=15.0, remaining_capacity_kg=15.0),
        Vehicle(id="van-1", capacity_kg=10.0, remaining_capacity_kg=10.0),
    ]

    main(demo_requests, demo_vehicles)
