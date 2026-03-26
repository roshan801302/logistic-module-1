"""Validator for incoming delivery request dicts."""

from __future__ import annotations

import uuid
from datetime import datetime

from .exceptions import ValidationError
from .models import DeliveryRequest

REQUIRED_FIELDS = ("weight_kg", "deadline", "customer_priority", "distance_km")


class Validator:
    def validate(self, raw: dict) -> DeliveryRequest:
        """
        Validate a raw delivery request dict and return a DeliveryRequest.

        Raises ValidationError with a descriptive message on any violation.
        Assigns a UUID and records submitted_at on success.
        """
        # Check all required fields are present
        for field in REQUIRED_FIELDS:
            if field not in raw:
                raise ValidationError(f"Missing required field: '{field}'")

        weight_kg = raw["weight_kg"]
        deadline = raw["deadline"]
        customer_priority = raw["customer_priority"]
        distance_km = raw["distance_km"]

        # Validate weight_kg > 0
        if not isinstance(weight_kg, (int, float)) or weight_kg <= 0:
            raise ValidationError("weight_kg must be > 0")

        # Validate deadline is in the future
        if not isinstance(deadline, datetime):
            raise ValidationError("deadline must be a datetime object")
        if deadline <= datetime.utcnow():
            raise ValidationError("deadline must be in the future")

        # Validate customer_priority is a positive integer
        if not isinstance(customer_priority, int) or isinstance(customer_priority, bool) or customer_priority <= 0:
            raise ValidationError("customer_priority must be a positive integer")

        # Validate distance_km >= 0
        if not isinstance(distance_km, (int, float)) or distance_km < 0:
            raise ValidationError("distance_km must be >= 0")

        return DeliveryRequest(
            id=str(uuid.uuid4()),
            weight_kg=float(weight_kg),
            deadline=deadline,
            customer_priority=customer_priority,
            distance_km=float(distance_km),
            submitted_at=datetime.utcnow(),
        )
