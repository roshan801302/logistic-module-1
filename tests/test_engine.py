"""Unit tests for PrioritizationEngine facade."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from logistics.engine import PrioritizationEngine
from logistics.exceptions import ValidationError
from logistics.models import DeliveryRequest, SortMode


def _future(hours: int = 1) -> datetime:
    return datetime.utcnow() + timedelta(hours=hours)


def _raw(weight: float = 5.0, priority: int = 1, distance: float = 10.0, hours: int = 1) -> dict:
    return {
        "weight_kg": weight,
        "deadline": _future(hours),
        "customer_priority": priority,
        "distance_km": distance,
    }


@pytest.fixture
def engine() -> PrioritizationEngine:
    return PrioritizationEngine()


# ---------------------------------------------------------------------------
# submit — stores requests
# ---------------------------------------------------------------------------

def test_submit_returns_delivery_request(engine):
    result = engine.submit(_raw())
    assert isinstance(result, DeliveryRequest)


def test_submit_stores_single_request(engine):
    engine.submit(_raw())
    assert len(engine.get_sorted(SortMode.DEADLINE)) == 1


def test_submit_stores_multiple_requests(engine):
    engine.submit(_raw(priority=2))
    engine.submit(_raw(priority=1))
    engine.submit(_raw(priority=3))
    assert len(engine.get_sorted(SortMode.DEADLINE)) == 3


def test_submit_assigns_unique_ids(engine):
    r1 = engine.submit(_raw())
    r2 = engine.submit(_raw())
    assert r1.id != r2.id


# ---------------------------------------------------------------------------
# submit — ValidationError propagation
# ---------------------------------------------------------------------------

def test_submit_propagates_validation_error_for_missing_field(engine):
    raw = _raw()
    del raw["weight_kg"]
    with pytest.raises(ValidationError):
        engine.submit(raw)


def test_submit_propagates_validation_error_for_invalid_weight(engine):
    with pytest.raises(ValidationError, match="weight_kg"):
        engine.submit(_raw(weight=-1.0))


def test_submit_propagates_validation_error_for_past_deadline(engine):
    raw = {**_raw(), "deadline": datetime.utcnow() - timedelta(seconds=1)}
    with pytest.raises(ValidationError, match="deadline"):
        engine.submit(raw)


def test_submit_invalid_does_not_store_request(engine):
    with pytest.raises(ValidationError):
        engine.submit(_raw(weight=0))
    assert len(engine.get_sorted(SortMode.DEADLINE)) == 0


# ---------------------------------------------------------------------------
# get_sorted — SortMode.DEADLINE (merge_sort)
# ---------------------------------------------------------------------------

def test_get_sorted_deadline_returns_deadline_ascending(engine):
    engine.submit(_raw(hours=3))
    engine.submit(_raw(hours=1))
    engine.submit(_raw(hours=2))
    result = engine.get_sorted(SortMode.DEADLINE)
    for i in range(len(result) - 1):
        assert result[i].deadline <= result[i + 1].deadline


def test_get_sorted_deadline_empty(engine):
    assert engine.get_sorted(SortMode.DEADLINE) == []


# ---------------------------------------------------------------------------
# get_sorted — SortMode.PRIORITY (quick_sort)
# ---------------------------------------------------------------------------

def test_get_sorted_priority_returns_priority_ascending(engine):
    engine.submit(_raw(priority=3))
    engine.submit(_raw(priority=1))
    engine.submit(_raw(priority=2))
    result = engine.get_sorted(SortMode.PRIORITY)
    for i in range(len(result) - 1):
        assert result[i].customer_priority <= result[i + 1].customer_priority


def test_get_sorted_priority_empty(engine):
    assert engine.get_sorted(SortMode.PRIORITY) == []


# ---------------------------------------------------------------------------
# get_sorted — SortMode.HEAP (heap_sort)
# ---------------------------------------------------------------------------

def test_get_sorted_heap_returns_priority_ascending(engine):
    engine.submit(_raw(priority=5))
    engine.submit(_raw(priority=2))
    engine.submit(_raw(priority=4))
    result = engine.get_sorted(SortMode.HEAP)
    for i in range(len(result) - 1):
        assert result[i].customer_priority <= result[i + 1].customer_priority


def test_get_sorted_heap_empty(engine):
    assert engine.get_sorted(SortMode.HEAP) == []


# ---------------------------------------------------------------------------
# get_sorted — does not mutate internal store
# ---------------------------------------------------------------------------

def test_get_sorted_does_not_mutate_store(engine):
    engine.submit(_raw(priority=3))
    engine.submit(_raw(priority=1))
    engine.get_sorted(SortMode.PRIORITY)
    # Submitting again should still see 3 total, not a sorted copy
    engine.submit(_raw(priority=2))
    assert len(engine.get_sorted(SortMode.DEADLINE)) == 3
