from datetime import datetime, timezone


class DateTimeUtils:
    """Time-related helpers. All in UTC."""

    @staticmethod
    def utc_now() -> datetime:
        """Current time in UTC (timezone-aware)."""
        return datetime.now(timezone.utc)
