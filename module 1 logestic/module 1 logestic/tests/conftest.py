"""Shared pytest configuration and Hypothesis strategies for the logistics test suite."""

from datetime import datetime, timedelta, timezone

import pytest
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Hypothesis strategy stubs — filled out as components are implemented
# ---------------------------------------------------------------------------

def future_datetime_strategy(min_offset_seconds: int = 1, max_offset_days: int = 365):
    """Strategy that generates UTC datetimes strictly in the future."""
    now = datetime.now(tz=timezone.utc)
    return st.integers(min_value=min_offset_seconds, max_value=max_offset_days * 86_400).map(
        lambda secs: now + timedelta(seconds=secs)
    )


def valid_request_dict_strategy():
    """Strategy that generates valid raw delivery-request dicts."""
    return st.fixed_dictionaries(
        {
            "weight_kg": st.floats(min_value=0.001, max_value=10_000.0, allow_nan=False, allow_infinity=False),
            "deadline": future_datetime_strategy(),
            "customer_priority": st.integers(min_value=1, max_value=1_000),
            "distance_km": st.floats(min_value=0.0, max_value=50_000.0, allow_nan=False, allow_infinity=False),
        }
    )


def delivery_request_strategy():
    """
    Strategy that generates DeliveryRequest instances.
    Imported lazily to avoid circular imports before models are implemented.
    """
    # Stub — will be populated in Task 2 once models.py exists.
    raise NotImplementedError("delivery_request_strategy is not yet implemented — complete Task 2 first.")
