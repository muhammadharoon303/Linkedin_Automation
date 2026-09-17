from typing import Dict, Optional
from .base import BasePlatformAdapter
from .linkedin import linkedin_adapter
from .tiktok import tiktok_adapter

class PublisherRegistry:
    def __init__(self):
        self._adapters: Dict[str, BasePlatformAdapter] = {
            "linkedin": linkedin_adapter,
            "tiktok": tiktok_adapter,
        }

    def get_adapter(self, platform: str) -> Optional[BasePlatformAdapter]:
        return self._adapters.get(platform.lower())

    def register_adapter(self, adapter: BasePlatformAdapter):
        self._adapters[adapter.platform_name.lower()] = adapter

publisher_registry = PublisherRegistry()
