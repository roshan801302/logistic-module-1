"""Unit tests for Scheduler.dispatch."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logistics.models import Assignment, DeliveryRequest, DispatchPlan, Vehicle
from logistics.scheduler import Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DT = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _req(id: str, weight_kg: float = 10.0) -> DeliveryRequest:
    return DeliveryRequest(
        id=id,
        weight_kg=weight_kg,
        deadline=_DT,
        customer_priority=1,
        distance_km=0.0,
        submitted_at=_DT,
    )


def _vehicle(id: str, capacity_kg: float) -> Vehicle:
    return Vehicle(id=id, capacity_kg=capacity_kg, remaining_capacity_kg=capacity_kg)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSchedulerBasicAssignment:
    def test_single_request_assigned_to_vehicle(self):
        scheduler = Scheduler()
        requests = [_req("r1", weight_kg=10.0)]
        vehicles = [_vehicle("v1", capacity_kg=100.0)]

        plan = scheduler.dispatch(requests, vehicles)

        assert len(plan.assignments) == 1
        assert plan.assignments[0].vehicle_id == "v1"
        assert plan.assignments[0].request_id == "r1"
        assert plan.deferred_request_ids == []

    def test_multiple_requests_assigned_in_order(self):
        scheduler = Scheduler()
        requests = [_req("r1", 10.0), _req("r2", 20.0), _req("r3", 5.0)]
        vehicles = [_vehicle("v1", 200.0)]

        plan = scheduler.dispatch(requests, vehicles)

        assert [a.request_id for a in plan.assignments] == ["r1", "r2", "r3"]
        assert plan.deferred_request_ids == []

    def test_requests_spread_across_vehicles(self):
        scheduler = Scheduler()
        # v1 can only hold r1; r2 spills to v2
        requests = [_req("r1", 50.0), _req("r2", 50.0)]
        vehicles = [_vehicle("v1", 50.0), _vehicle("v2", 100.0)]

        plan = scheduler.dispatch(requests, vehicles)

        assert len(plan.assignments) == 2
        assert plan.assignments[0] == Assignment(vehicle_id="v1", request_id="r1")
        assert plan.assignments[1] == Assignment(vehicle_id="v2", request_id="r2")
        assert plan.deferred_request_ids == []


class TestSchedulerDeferral:
    def test_request_deferred_when_no_vehicle_has_capacity(self):
        scheduler = Scheduler()
        requests = [_req("r1", weight_kg=200.0)]
        vehicles = [_vehicle("v1", capacity_kg=50.0)]

        plan = scheduler.dispatch(requests, vehicles)

        assert plan.assignments == []
        assert plan.deferred_request_ids == ["r1"]

    def test_partial_deferral(self):
        scheduler = Scheduler()
        requests = [_req("r1", 10.0), _req("r2", 999.0)]
        vehicles = [_vehicle("v1", 50.0)]

        plan = scheduler.dispatch(requests, vehicles)

        assert len(plan.assignments) == 1
        assert plan.assignments[0].request_id == "r1"
        assert plan.deferred_request_ids == ["r2"]

    def test_all_deferred_when_no_vehicles(self):
        scheduler = Scheduler()
        requests = [_req("r1"), _req("r2")]
        plan = Scheduler().dispatch(requests, [])

        assert plan.assignments == []
        assert plan.deferred_request_ids == ["r1", "r2"]

    def test_deferral_logged(self, caplog):
        import logging
        scheduler = Scheduler()
        requests = [_req("heavy", weight_kg=500.0)]
        vehicles = [_vehicle("v1", capacity_kg=10.0)]

        with caplog.at_level(logging.WARNING, logger="logistics.scheduler"):
            scheduler.dispatch(requests, vehicles)

        assert any("heavy" in record.message for record in caplog.records)


class TestSchedulerCapacityDecrement:
    def test_remaining_capacity_decremented_after_assignment(self):
        scheduler = Scheduler()
        requests = [_req("r1", 30.0)]
        v = _vehicle("v1", 100.0)

        scheduler.dispatch(requests, [v])

        assert v.remaining_capacity_kg == 70.0

    def test_capacity_decremented_across_multiple_assignments(self):
        scheduler = Scheduler()
        requests = [_req("r1", 20.0), _req("r2", 15.0), _req("r3", 10.0)]
        v = _vehicle("v1", 100.0)

        scheduler.dispatch(requests, [v])

        assert v.remaining_capacity_kg == 55.0

    def test_exact_capacity_fit_assigns_and_zeroes_remaining(self):
        scheduler = Scheduler()
        requests = [_req("r1", 50.0)]
        v = _vehicle("v1", 50.0)

        plan = scheduler.dispatch(requests, [v])

        assert plan.deferred_request_ids == []
        assert v.remaining_capacity_kg == 0.0

    def test_request_just_over_capacity_is_deferred(self):
        scheduler = Scheduler()
        requests = [_req("r1", 50.1)]
        v = _vehicle("v1", 50.0)

        plan = scheduler.dispatch(requests, [v])

        assert plan.assignments == []
        assert plan.deferred_request_ids == ["r1"]
        # capacity must not have changed
        assert v.remaining_capacity_kg == 50.0


class TestSchedulerEmptyInputs:
    def test_empty_requests_returns_empty_plan(self):
        scheduler = Scheduler()
        vehicles = [_vehicle("v1", 100.0)]

        plan = scheduler.dispatch([], vehicles)

        assert plan.assignments == []
        assert plan.deferred_request_ids == []

    def test_empty_requests_and_vehicles(self):
        plan = Scheduler().dispatch([], [])

        assert plan.assignments == []
        assert plan.deferred_request_ids == []
