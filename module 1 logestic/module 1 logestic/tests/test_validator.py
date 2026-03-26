"""Unit tests for Validator — covers each validation error path."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from logistics.exceptions import ValidationError
from logistics.validator import Validator


@pytest.fixture
def validator():
    return Validator()


def _future() -> datetime:
    return datetime.utcnow() + timedelta(hours=1)


def _valid_raw() -> dict:
    return {
        "weight_kg": 5.0,
        "deadline": _future(),
        "customer_priority": 1,
        "distance_km": 10.0,
    }


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_request_returns_delivery_request(validator):
    raw = _valid_raw()
    result = validator.validate(raw)
    assert result.weight_kg == 5.0
    assert result.customer_priority == 1
    assert result.distance_km == 10.0
    assert result.id  # UUID assigned
    assert result.submitted_at is not None


def test_valid_request_assigns_unique_ids(validator):
    ids = {validator.validate(_valid_raw()).id for _ in range(10)}
    assert len(ids) == 10


def test_distance_km_zero_is_valid(validator):
    raw = {**_valid_raw(), "distance_km": 0.0}
    result = validator.validate(raw)
    assert result.distance_km == 0.0


# ---------------------------------------------------------------------------
# Missing fields
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing_field", ["weight_kg", "deadline", "customer_priority", "distance_km"])
def test_missing_field_raises_validation_error(validator, missing_field):
    raw = _valid_raw()
    del raw[missing_field]
    with pytest.raises(ValidationError, match=missing_field):
        validator.validate(raw)


# ---------------------------------------------------------------------------
# weight_kg validation
# ---------------------------------------------------------------------------

def test_weight_zero_raises_validation_error(validator):
    raw = {**_valid_raw(), "weight_kg": 0}
    with pytest.raises(ValidationError, match="weight_kg"):
        validator.validate(raw)


def test_weight_negative_raises_validation_error(validator):
    raw = {**_valid_raw(), "weight_kg": -1.0}
    with pytest.raises(ValidationError, match="weight_kg"):
        validator.validate(raw)


# ---------------------------------------------------------------------------
# deadline validation
# ---------------------------------------------------------------------------

def test_past_deadline_raises_validation_error(validator):
    raw = {**_valid_raw(), "deadline": datetime.utcnow() - timedelta(seconds=1)}
    with pytest.raises(ValidationError, match="deadline"):
        validator.validate(raw)


def test_deadline_now_raises_validation_error(validator):
    # deadline equal to utcnow() should also fail (must be strictly future)
    raw = {**_valid_raw(), "deadline": datetime.utcnow() - timedelta(microseconds=1)}
    with pytest.raises(ValidationError, match="deadline"):
        validator.validate(raw)


def test_non_datetime_deadline_raises_validation_error(validator):
    raw = {**_valid_raw(), "deadline": "2099-01-01T00:00:00"}
    with pytest.raises(ValidationError, match="deadline"):
        validator.validate(raw)


# ---------------------------------------------------------------------------
# customer_priority validation
# ---------------------------------------------------------------------------

def test_priority_zero_raises_validation_error(validator):
    raw = {**_valid_raw(), "customer_priority": 0}
    with pytest.raises(ValidationError, match="customer_priority"):
        validator.validate(raw)


def test_priority_negative_raises_validation_error(validator):
    raw = {**_valid_raw(), "customer_priority": -5}
    with pytest.raises(ValidationError, match="customer_priority"):
        validator.validate(raw)


def test_priority_float_raises_validation_error(validator):
    raw = {**_valid_raw(), "customer_priority": 1.5}
    with pytest.raises(ValidationError, match="customer_priority"):
        validator.validate(raw)


def test_priority_bool_raises_validation_error(validator):
    # bool is a subclass of int in Python; True == 1 but should not be accepted
    raw = {**_valid_raw(), "customer_priority": True}
    with pytest.raises(ValidationError, match="customer_priority"):
        validator.validate(raw)


# ---------------------------------------------------------------------------
# distance_km validation
# ---------------------------------------------------------------------------

def test_negative_distance_raises_validation_error(validator):
    raw = {**_valid_raw(), "distance_km": -0.1}
    with pytest.raises(ValidationError, match="distance_km"):
        validator.validate(raw)
