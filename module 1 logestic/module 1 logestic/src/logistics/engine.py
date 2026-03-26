"""PrioritizationEngine — facade wiring Validator and Sorter together."""

from __future__ import annotations

from .models import DeliveryRequest, SortMode
from .sorter import heap_sort, merge_sort, quick_sort
from .validator import Validator


class PrioritizationEngine:
    """Facade that validates, stores, and sorts delivery requests."""

    def __init__(self) -> None:
        self._validator = Validator()
        self._requests: list[DeliveryRequest] = []

    def submit(self, raw: dict) -> DeliveryRequest:
        """Validate *raw* and store the resulting DeliveryRequest.

        Raises ValidationError (propagated from Validator) on invalid input.
        """
        request = self._validator.validate(raw)
        self._requests.append(request)
        return request

    def get_sorted(self, mode: SortMode) -> list[DeliveryRequest]:
        """Return all accepted requests sorted according to *mode*.

        SortMode.DEADLINE → merge_sort (stable, by deadline ascending)
        SortMode.PRIORITY → quick_sort (by customer_priority ascending)
        SortMode.HEAP     → heap_sort  (by customer_priority ascending)
        """
        if mode is SortMode.DEADLINE:
            return merge_sort(self._requests)
        if mode is SortMode.PRIORITY:
            return quick_sort(self._requests)
        if mode is SortMode.HEAP:
            return heap_sort(self._requests)
        raise ValueError(f"Unknown SortMode: {mode!r}")  # pragma: no cover
