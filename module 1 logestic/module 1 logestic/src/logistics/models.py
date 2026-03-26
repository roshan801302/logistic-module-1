from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SortMode(Enum):
    DEADLINE = "deadline"   # stable sort by deadline (merge sort)
    PRIORITY = "priority"   # sort by customer_priority (quick sort)
    HEAP = "heap"           # sort by customer_priority (heap sort)


@dataclass(frozen=True)
class DeliveryRequest:
    id: str
    weight_kg: float
    deadline: datetime
    customer_priority: int
    distance_km: float
    submitted_at: datetime


@dataclass
class Vehicle:
    id: str
    capacity_kg: float
    remaining_capacity_kg: float


@dataclass
class Assignment:
    vehicle_id: str
    request_id: str


@dataclass
class DispatchPlan:
    assignments: list[Assignment]
    deferred_request_ids: list[str]


@dataclass
class BenchmarkResult:
    algorithm: str
    dataset_size: int
    elapsed_ms: float | None  # None means timeout
