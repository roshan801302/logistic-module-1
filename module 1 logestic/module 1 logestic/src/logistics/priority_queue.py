"""Min-heap based PriorityQueue for DeliveryRequests."""
from __future__ import annotations

import heapq
from typing import List, Tuple

from logistics.exceptions import EmptyQueueError
from logistics.models import DeliveryRequest


class PriorityQueue:
    """Min-heap priority queue ordered by customer_priority (lowest value = highest priority).

    insert and extract_min both run in O(log n).
    """

    def __init__(self) -> None:
        # Heap entries: (customer_priority, tie_breaker, DeliveryRequest)
        # tie_breaker is an insertion counter to ensure stable ordering when
        # customer_priority values are equal and to avoid comparing DeliveryRequest objects.
        self._heap: List[Tuple[int, int, DeliveryRequest]] = []
        self._counter: int = 0

    def insert(self, request: DeliveryRequest) -> None:
        """Insert a DeliveryRequest in O(log n)."""
        heapq.heappush(self._heap, (request.customer_priority, self._counter, request))
        self._counter += 1

    def extract_min(self) -> DeliveryRequest:
        """Remove and return the DeliveryRequest with the lowest customer_priority.

        Raises EmptyQueueError if the queue is empty.
        """
        if not self._heap:
            raise EmptyQueueError("Cannot extract from an empty PriorityQueue.")
        _, _, request = heapq.heappop(self._heap)
        return request

    def peek(self) -> DeliveryRequest:
        """Return (without removing) the DeliveryRequest with the lowest customer_priority.

        Raises EmptyQueueError if the queue is empty.
        """
        if not self._heap:
            raise EmptyQueueError("Cannot peek into an empty PriorityQueue.")
        _, _, request = self._heap[0]
        return request

    def __len__(self) -> int:
        """Return the current number of elements in the queue."""
        return len(self._heap)
