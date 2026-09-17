from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from ...models.post import Post
from ...models.account import SocialAccount

@dataclass
class PublishResult:
    success: bool
    platform_post_id: Optional[str] = None
    error: Optional[str] = None
    requires_manual_action: bool = False
    details: Optional[str] = None

class BasePlatformAdapter(ABC):
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Returns the platform key e.g. 'linkedin', 'tiktok'."""
        pass

    @abstractmethod
    async def publish(self, post: Post, account: Optional[SocialAccount]) -> PublishResult:
        """Publishes the post to the platform using official APIs."""
        pass
