"""
Time utilities for ChainPulse
"""
import time
from datetime import datetime, timezone
from typing import Union

def get_current_timestamp() -> int:
    """Get current timestamp in seconds"""
    return int(time.time())

def get_current_time() -> int:
    """Get current time (alias for get_current_timestamp)"""
    return get_current_timestamp()

def get_current_timestamp_ms() -> int:
    """Get current timestamp in milliseconds"""
    return int(time.time() * 1000)

def get_current_datetime() -> datetime:
    """Get current datetime in UTC"""
    return datetime.now(timezone.utc)

def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """Convert timestamp to datetime"""
    if timestamp > 1e10:  # If timestamp is in milliseconds
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(timestamp, timezone.utc)

def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to timestamp"""
    return int(dt.timestamp())

def format_timestamp(timestamp: Union[int, float], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp as string"""
    dt = timestamp_to_datetime(timestamp)
    return dt.strftime(format_str)

def get_timeframe_seconds(timeframe: str) -> int:
    """Convert timeframe string to seconds"""
    timeframe_map = {
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '30m': 1800,
        '1h': 3600,
        '4h': 14400,
        '1d': 86400,
        '1w': 604800
    }
    return timeframe_map.get(timeframe, 3600)  # Default to 1 hour

def sleep_until_next_interval(interval_seconds: int):
    """Sleep until the next interval"""
    current_time = get_current_timestamp()
    next_interval = ((current_time // interval_seconds) + 1) * interval_seconds
    sleep_time = next_interval - current_time
    if sleep_time > 0:
        time.sleep(sleep_time)