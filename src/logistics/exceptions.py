"""Custom exceptions for the Logistics Network Optimizer."""


class LogisticsError(Exception):
    """Base exception for all logistics system errors."""


class ValidationError(LogisticsError):
    """Raised when a delivery request fails validation."""


class EmptyQueueError(LogisticsError):
    """Raised when extract_min or peek is called on an empty PriorityQueue."""
