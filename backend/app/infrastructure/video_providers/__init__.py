"""
Video Provider Implementations (Adapters).

Contains concrete implementations of the IVideoProvider interface.
Each adapter wraps a specific video service provider.

Available Providers:
- DailyVideoProvider: Daily.co video API
- MockVideoProvider: For testing without API calls
"""

from .daily_provider import DailyVideoProvider
from .mock_provider import MockVideoProvider

__all__ = [
    "DailyVideoProvider",
    "MockVideoProvider",
]
