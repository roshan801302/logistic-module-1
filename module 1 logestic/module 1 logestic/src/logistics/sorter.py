from __future__ import annotations

import random

from logistics.models import DeliveryRequest


def quick_sort(requests: list[DeliveryRequest]) -> list[DeliveryRequest]:
    """Sort by customer_priority ascending. O(n log n) average case.

    Uses a randomised pivot to avoid worst-case O(n²) on sorted inputs.
    Returns a new list; does not mutate the input.
    Quick Sort is not guaranteed to be stable.
    """
    if len(requests) <= 1:
        return list(requests)

    lst = list(requests)
    _quick_sort_inplace(lst, 0, len(lst) - 1)
    return lst


def _quick_sort_inplace(
    lst: list[DeliveryRequest],
    low: int,
    high: int,
) -> None:
    if low < high:
        pivot_idx = _partition(lst, low, high)
        _quick_sort_inplace(lst, low, pivot_idx - 1)
        _quick_sort_inplace(lst, pivot_idx + 1, high)


def _partition(lst: list[DeliveryRequest], low: int, high: int) -> int:
    # Randomised pivot: swap a random element into the high position
    rand_idx = random.randint(low, high)
    lst[rand_idx], lst[high] = lst[high], lst[rand_idx]

    pivot = lst[high].customer_priority
    i = low - 1
    for j in range(low, high):
        if lst[j].customer_priority <= pivot:
            i += 1
            lst[i], lst[j] = lst[j], lst[i]
    lst[i + 1], lst[high] = lst[high], lst[i + 1]
    return i + 1


def merge_sort(requests: list[DeliveryRequest]) -> list[DeliveryRequest]:
    """Stable sort by deadline ascending. O(n log n) worst case.

    Returns a new list; does not mutate the input.
    """
    if len(requests) <= 1:
        return list(requests)

    mid = len(requests) // 2
    left = merge_sort(requests[:mid])
    right = merge_sort(requests[mid:])
    return _merge(left, right)


def _merge(
    left: list[DeliveryRequest],
    right: list[DeliveryRequest],
) -> list[DeliveryRequest]:
    result: list[DeliveryRequest] = []
    i = j = 0
    while i < len(left) and j < len(right):
        # Use <= to preserve stability: left element wins on equal deadline
        if left[i].deadline <= right[j].deadline:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heap_sort(requests: list[DeliveryRequest]) -> list[DeliveryRequest]:
    """Sort by customer_priority ascending using a max-heap. O(n log n).

    Builds a max-heap (negated priority so the largest value = lowest priority
    sits at the root), then repeatedly extracts the max to produce an
    ascending-priority result.
    Returns a new list; does not mutate the input.
    """
    if len(requests) <= 1:
        return list(requests)

    lst = list(requests)
    n = len(lst)

    # Build max-heap in-place (heapify)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(lst, i, n)

    # Extract elements one by one: swap root (max) to end, shrink heap
    for end in range(n - 1, 0, -1):
        lst[0], lst[end] = lst[end], lst[0]
        _sift_down(lst, 0, end)

    return lst


def _sift_down(lst: list[DeliveryRequest], root: int, end: int) -> None:
    """Sift the element at *root* down to restore the max-heap property.

    The heap covers indices [0, end).  Max-heap key is customer_priority
    (higher value = higher in the heap).
    """
    while True:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < end and lst[left].customer_priority > lst[largest].customer_priority:
            largest = left
        if right < end and lst[right].customer_priority > lst[largest].customer_priority:
            largest = right

        if largest == root:
            break

        lst[root], lst[largest] = lst[largest], lst[root]
        root = largest


def insertion_sort(requests: list[DeliveryRequest]) -> list[DeliveryRequest]:
    """Sort by customer_priority ascending using Insertion Sort. O(n²) baseline.

    Returns a new list; does not mutate the input.
    """
    lst = list(requests)
    for i in range(1, len(lst)):
        key = lst[i]
        j = i - 1
        while j >= 0 and lst[j].customer_priority > key.customer_priority:
            lst[j + 1] = lst[j]
            j -= 1
        lst[j + 1] = key
    return lst
