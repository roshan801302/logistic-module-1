"""Unit tests for Benchmarker."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from logistics.benchmarker import Benchmarker
from logistics.models import BenchmarkResult

_ALGORITHM_NAMES = {"merge_sort", "quick_sort", "heap_sort", "insertion_sort"}


class TestBenchmarkerResultCount:
    def test_four_results_returned_for_single_dataset_size(self):
        """For n=100, exactly four BenchmarkResult objects are returned (one per algorithm)."""
        benchmarker = Benchmarker()
        results = benchmarker.run([100])

        assert len(results) == 4
        returned_algos = {r.algorithm for r in results}
        assert returned_algos == _ALGORITHM_NAMES

    def test_all_results_have_correct_dataset_size(self):
        benchmarker = Benchmarker()
        results = benchmarker.run([100])

        assert all(r.dataset_size == 100 for r in results)

    def test_results_count_scales_with_dataset_sizes(self):
        """For k dataset sizes, 4*k results are returned."""
        benchmarker = Benchmarker()
        results = benchmarker.run([10, 50, 100])

        assert len(results) == 12  # 4 algorithms × 3 sizes

    def test_elapsed_ms_is_non_negative_for_fast_run(self):
        benchmarker = Benchmarker()
        results = benchmarker.run([100])

        for r in results:
            assert r.elapsed_ms is None or r.elapsed_ms >= 0.0


class TestBenchmarkerTimeout:
    def test_timeout_recorded_as_none(self):
        """When a run exceeds timeout_ms, elapsed_ms should be None."""
        benchmarker = Benchmarker()

        # Simulate: first call returns t=0, second call returns a value far beyond timeout
        call_count = 0
        timeout_ms = 10.0  # 10 ms timeout

        def fake_perf_counter():
            nonlocal call_count
            call_count += 1
            # Odd calls = start time (0.0), even calls = end time (far in future)
            if call_count % 2 == 1:
                return 0.0
            else:
                return 1.0  # 1 second elapsed >> 10 ms timeout

        with patch("logistics.benchmarker.time.perf_counter", side_effect=fake_perf_counter):
            results = benchmarker.run([100], timeout_ms=timeout_ms)

        timed_out = [r for r in results if r.elapsed_ms is None]
        assert len(timed_out) == 4  # all four algorithms should time out

    def test_no_timeout_when_run_is_fast(self):
        """When runs complete within timeout, elapsed_ms should be a float."""
        benchmarker = Benchmarker()
        # Very generous timeout — all algorithms on n=10 should finish well within it
        results = benchmarker.run([10], timeout_ms=30_000)

        for r in results:
            assert r.elapsed_ms is not None
            assert isinstance(r.elapsed_ms, float)
