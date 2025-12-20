"""
Video Provider Implementations (Adapters).

Contains concrete implementations of the IVideoProvider interface.
Each adapter wraps a specific video service provider.

Available Providers:
- DailyVideoProvider: Daily.co video API
- HundredMsVideoProvider: 100ms video API
- MockVideoProvider: For testing without API calls

Provider Selection:
    Configure VIDEO_PROVIDER in .env file:
    - "daily": Uses Daily.co
    - "hundredms": Uses 100ms
    - "mock": Uses mock provider

Architecture:
    All providers implement the IVideoProvider interface (Port),
    making them interchangeable adapters. The application code
    depends only on the interface, not specific implementations.

    To add a new provider (e.g., Jitsi):
    1. Create jitsi_provider.py implementing IVideoProvider
    2. Add to this __init__.py exports
    3. Add configuration settings in config.py
    4. Add provider selection in dependencies.py
"""

from .daily_provider import DailyVideoProvider
from .hundredms_provider import HundredMsVideoProvider
from .mock_provider import MockVideoProvider

__all__ = [
    "DailyVideoProvider",
    "HundredMsVideoProvider",
    "MockVideoProvider",
]
