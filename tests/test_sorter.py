"""Unit tests for merge_sort and quick_sort in sorter.py."""
from datetime import datetime, timezone

import pytest

from logistics.models import DeliveryRequest
from logistics.sorter import merge_sort, quick_sort


def _req(id: str, deadline: datetime, submitted_offset: int = 0, priority: int = 1) -> DeliveryRequest:
    """Helper to build a minimal DeliveryRequest."""
    return DeliveryRequest(
        id=id,
        weight_kg=1.0,
        deadline=deadline,
        customer_priority=priority,
        distance_km=0.0,
        submitted_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


DT = datetime(2024, 6, 1, tzinfo=timezone.utc)
DT2 = datetime(2024, 6, 2, tzinfo=timezone.utc)
DT3 = datetime(2024, 6, 3, tzinfo=timezone.utc)


class TestMergeSortEdgeCases:
    def test_empty_list_returns_empty(self):
        assert merge_sort([]) == []

    def test_single_element_returns_same_element(self):
        req = _req("a", DT)
        result = merge_sort([req])
        assert result == [req]

    def test_returns_new_list(self):
        req = _req("a", DT)
        original = [req]
        result = merge_sort(original)
        assert result is not original


class TestMergeSortOrdering:
    def test_already_sorted_list(self):
        reqs = [_req("a", DT), _req("b", DT2), _req("c", DT3)]
        assert merge_sort(reqs) == reqs

    def test_reverse_sorted_list(self):
        reqs = [_req("c", DT3), _req("b", DT2), _req("a", DT)]
        result = merge_sort(reqs)
        assert [r.id for r in result] == ["a", "b", "c"]

    def test_unsorted_list(self):
        reqs = [_req("b", DT2), _req("a", DT), _req("c", DT3)]
        result = merge_sort(reqs)
        assert [r.id for r in result] == ["a", "b", "c"]

    def test_output_is_deadline_ascending(self):
        reqs = [_req("c", DT3), _req("a", DT), _req("b", DT2)]
        result = merge_sort(reqs)
        for i in range(len(result) - 1):
            assert result[i].deadline <= result[i + 1].deadline


class TestMergeSortStability:
    def test_equal_deadlines_preserve_original_order(self):
        # Two requests with the same deadline — original order must be preserved
        r1 = _req("first", DT)
        r2 = _req("second", DT)
        result = merge_sort([r1, r2])
        assert [r.id for r in result] == ["first", "second"]

    def test_equal_deadlines_reversed_input_preserves_order(self):
        r1 = _req("x", DT)
        r2 = _req("y", DT)
        r3 = _req("z", DT)
        result = merge_sort([r1, r2, r3])
        assert [r.id for r in result] == ["x", "y", "z"]

    def test_mixed_deadlines_stability(self):
        # r1 and r3 share DT; r2 has DT2
        r1 = _req("r1", DT)
        r2 = _req("r2", DT2)
        r3 = _req("r3", DT)
        result = merge_sort([r1, r2, r3])
        # r1 and r3 both have DT (earlier), r2 has DT2 (later)
        assert result[0].id == "r1"
        assert result[1].id == "r3"
        assert result[2].id == "r2"


class TestQuickSortEdgeCases:
    def test_empty_list_returns_empty(self):
        assert quick_sort([]) == []

    def test_single_element_returns_same_element(self):
        req = _req("a", DT, priority=2)
        result = quick_sort([req])
        assert result == [req]

    def test_returns_new_list(self):
        req = _req("a", DT, priority=1)
        original = [req]
        result = quick_sort(original)
        assert result is not original

    def test_does_not_mutate_input(self):
        reqs = [_req("b", DT, priority=3), _req("a", DT, priority=1)]
        original_ids = [r.id for r in reqs]
        quick_sort(reqs)
        assert [r.id for r in reqs] == original_ids


class TestQuickSortOrdering:
    def test_already_sorted_by_priority(self):
        reqs = [_req("a", DT, priority=1), _req("b", DT, priority=2), _req("c", DT, priority=3)]
        result = quick_sort(reqs)
        assert [r.customer_priority for r in result] == [1, 2, 3]

    def test_reverse_sorted_by_priority(self):
        reqs = [_req("c", DT, priority=3), _req("b", DT, priority=2), _req("a", DT, priority=1)]
        result = quick_sort(reqs)
        assert [r.customer_priority for r in result] == [1, 2, 3]

    def test_unsorted_priorities(self):
        reqs = [_req("b", DT, priority=2), _req("a", DT, priority=1), _req("c", DT, priority=3)]
        result = quick_sort(reqs)
        assert [r.customer_priority for r in result] == [1, 2, 3]

    def test_output_is_priority_ascending(self):
        reqs = [
            _req("d", DT, priority=4),
            _req("a", DT, priority=1),
            _req("c", DT, priority=3),
            _req("b", DT, priority=2),
        ]
        result = quick_sort(reqs)
        for i in range(len(result) - 1):
            assert result[i].customer_priority <= result[i + 1].customer_priority


from logistics.sorter import heap_sort


class TestHeapSortEdgeCases:
    def test_empty_list_returns_empty(self):
        assert heap_sort([]) == []

    def test_single_element_returns_same_element(self):
        req = _req("a", DT, priority=5)
        result = heap_sort([req])
        assert result == [req]

    def test_returns_new_list(self):
        req = _req("a", DT, priority=1)
        original = [req]
        result = heap_sort(original)
        assert result is not original

    def test_does_not_mutate_input(self):
        reqs = [_req("b", DT, priority=3), _req("a", DT, priority=1)]
        original_ids = [r.id for r in reqs]
        heap_sort(reqs)
        assert [r.id for r in reqs] == original_ids


class TestHeapSortOrdering:
    def test_already_sorted_by_priority(self):
        reqs = [_req("a", DT, priority=1), _req("b", DT, priority=2), _req("c", DT, priority=3)]
        result = heap_sort(reqs)
        assert [r.customer_priority for r in result] == [1, 2, 3]

    def test_reverse_sorted_by_priority(self):
        reqs = [_req("c", DT, priority=3), _req("b", DT, priority=2), _req("a", DT, priority=1)]
        result = heap_sort(reqs)
        assert [r.customer_priority for r in result] == [1, 2, 3]

    def test_unsorted_priorities(self):
        reqs = [_req("b", DT, priority=2), _req("a", DT, priority=1), _req("c", DT, priority=3)]
        result = heap_sort(reqs)
        assert [r.customer_priority for r in result] == [1, 2, 3]

    def test_output_is_priority_ascending(self):
        reqs = [
            _req("d", DT, priority=4),
            _req("a", DT, priority=1),
            _req("c", DT, priority=3),
            _req("b", DT, priority=2),
        ]
        result = heap_sort(reqs)
        for i in range(len(result) - 1):
            assert result[i].customer_priority <= result[i + 1].customer_priority

    def test_equal_priorities(self):
        reqs = [_req("a", DT, priority=2), _req("b", DT, priority=2), _req("c", DT, priority=2)]
        result = heap_sort(reqs)
        assert all(r.customer_priority == 2 for r in result)
        assert len(result) == 3

    def test_output_is_permutation_of_input(self):
        reqs = [
            _req("x", DT, priority=5),
            _req("y", DT, priority=1),
            _req("z", DT, priority=3),
        ]
        result = heap_sort(reqs)
        assert sorted(r.id for r in result) == sorted(r.id for r in reqs)
