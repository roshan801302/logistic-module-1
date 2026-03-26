"""Benchmarker: measures wall-clock time for each sorting algorithm at varying dataset sizes."""
from __future__ import annotations

import random
import time
import uuid
from datetime import datetime, timedelta, timezone

from logistics.models import BenchmarkResult, DeliveryRequest
from logistics.sorter import heap_sort, insertion_sort, merge_sort, quick_sort

_ALGORITHMS: list[tuple[str, object]] = [
    ("merge_sort", merge_sort),
    ("quick_sort", quick_sort),
    ("heap_sort", heap_sort),
    ("insertion_sort", insertion_sort),
]


def _generate_requests(n: int) -> list[DeliveryRequest]:
    """Generate *n* random DeliveryRequest objects."""
    now = datetime.now(tz=timezone.utc)
    return [
        DeliveryRequest(
            id=str(uuid.uuid4()),
            weight_kg=random.uniform(0.1, 100.0),
            deadline=now + timedelta(seconds=random.randint(1, 86_400)),
            customer_priority=random.randint(1, 1_000),
            distance_km=random.uniform(0.0, 500.0),
            submitted_at=now,
        )
        for _ in range(n)
    ]


class Benchmarker:
    def run(
        self,
        dataset_sizes: list[int],
        timeout_ms: float = 30_000,
    ) -> list[BenchmarkResult]:
        """Time each algorithm on randomly generated datasets of the given sizes.

        For each (algorithm, dataset_size) pair:
        - Generates a fresh random dataset.
        - Times the sort using time.perf_counter.
        - Records elapsed_ms = None if the run exceeds timeout_ms.

        Returns one BenchmarkResult per (algorithm, dataset_size) combination.
        """
        results: list[BenchmarkResult] = []
        timeout_s = timeout_ms / 1_000.0

        for n in dataset_sizes:
            requests = _generate_requests(n)
            for algo_name, algo_fn in _ALGORITHMS:
                dataset = list(requests)  # fresh copy per algorithm
                start = time.perf_counter()
                algo_fn(dataset)  # type: ignore[operator]
                elapsed_s = time.perf_counter() - start

                if elapsed_s > timeout_s:
                    elapsed_ms: float | None = None
                else:
                    elapsed_ms = elapsed_s * 1_000.0

                results.append(
                    BenchmarkResult(
                        algorithm=algo_name,
                        dataset_size=n,
                        elapsed_ms=elapsed_ms,
                    )
                )

        return results
