"""Unit tests for PriorityQueue (task 6.2).

Covers:
- EmptyQueueError on extract_min and peek when queue is empty
- insert and extract_min ordering (min customer_priority first)
- __len__ reflects queue size correctly
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logistics.exceptions import EmptyQueueError
from logistics.models import DeliveryRequest
from logistics.priority_queue import PriorityQueue


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DT = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _req(id: str, priority: int) -> DeliveryRequest:
    return DeliveryRequest(
        id=id,
        weight_kg=1.0,
        deadline=_DT,
        customer_priority=priority,
        distance_km=0.0,
        submitted_at=_DT,
    )


# ---------------------------------------------------------------------------
# EmptyQueueError tests
# ---------------------------------------------------------------------------

class TestEmptyQueueError:
    def test_extract_min_raises_on_empty_queue(self):
        pq = PriorityQueue()
        with pytest.raises(EmptyQueueError):
            pq.extract_min()

    def test_peek_raises_on_empty_queue(self):
        pq = PriorityQueue()
        with pytest.raises(EmptyQueueError):
            pq.peek()

    def test_extract_min_raises_after_all_elements_removed(self):
        pq = PriorityQueue()
        pq.insert(_req("a", 1))
        pq.extract_min()
        with pytest.raises(EmptyQueueError):
            pq.extract_min()

    def test_peek_raises_after_all_elements_removed(self):
        pq = PriorityQueue()
        pq.insert(_req("a", 1))
        pq.extract_min()
        with pytest.raises(EmptyQueueError):
            pq.peek()


# ---------------------------------------------------------------------------
# insert / extract_min ordering tests
# ---------------------------------------------------------------------------

class TestInsertExtractOrdering:
    def test_single_insert_extract_returns_same_element(self):
        pq = PriorityQueue()
        req = _req("a", 5)
        pq.insert(req)
        assert pq.extract_min() is req

    def test_extract_min_returns_lowest_priority_value(self):
        pq = PriorityQueue()
        pq.insert(_req("b", 3))
        pq.insert(_req("a", 1))
        pq.insert(_req("c", 2))
        result = pq.extract_min()
        assert result.customer_priority == 1

    def test_extract_min_ordering_ascending(self):
        pq = PriorityQueue()
        for priority in [4, 2, 5, 1, 3]:
            pq.insert(_req(str(priority), priority))

        extracted = [pq.extract_min().customer_priority for _ in range(5)]
        assert extracted == [1, 2, 3, 4, 5]

    def test_extract_min_with_equal_priorities(self):
        pq = PriorityQueue()
        pq.insert(_req("x", 2))
        pq.insert(_req("y", 2))
        pq.insert(_req("z", 2))
        # All have same priority — all should be extractable without error
        results = [pq.extract_min().customer_priority for _ in range(3)]
        assert results == [2, 2, 2]

    def test_peek_returns_min_without_removing(self):
        pq = PriorityQueue()
        pq.insert(_req("b", 3))
        pq.insert(_req("a", 1))
        assert pq.peek().customer_priority == 1
        assert len(pq) == 2  # still 2 elements

    def test_peek_consistent_with_extract_min(self):
        pq = PriorityQueue()
        pq.insert(_req("b", 5))
        pq.insert(_req("a", 2))
        assert pq.peek() is pq.extract_min()

    def test_extract_all_returns_sorted_order(self):
        priorities = [7, 3, 9, 1, 4, 6, 2, 8, 5]
        pq = PriorityQueue()
        for p in priorities:
            pq.insert(_req(str(p), p))

        extracted = []
        while len(pq) > 0:
            extracted.append(pq.extract_min().customer_priority)

        assert extracted == sorted(priorities)


# ---------------------------------------------------------------------------
# __len__ tests
# ---------------------------------------------------------------------------

class TestLen:
    def test_empty_queue_has_len_zero(self):
        assert len(PriorityQueue()) == 0

    def test_len_increases_with_inserts(self):
        pq = PriorityQueue()
        for i in range(1, 6):
            pq.insert(_req(str(i), i))
            assert len(pq) == i

    def test_len_decreases_with_extracts(self):
        pq = PriorityQueue()
        for i in range(1, 4):
            pq.insert(_req(str(i), i))

        for remaining in [2, 1, 0]:
            pq.extract_min()
            assert len(pq) == remaining

    def test_len_unaffected_by_peek(self):
        pq = PriorityQueue()
        pq.insert(_req("a", 1))
        pq.insert(_req("b", 2))
        pq.peek()
        assert len(pq) == 2
