import asyncio
from typing import List
from .schemas import PostCreate, PostResult
from .connectors.mastodon import MastodonConnector
from .connectors.bluesky import BlueskyConnector
from .connectors.telegram import TelegramConnector
from .connectors.facebook import FacebookConnector
from .connectors.linkedin import LinkedInConnector

class PostDispatcher:
    def __init__(self):
        self.connectors = {
            "mastodon": MastodonConnector(),
            "bluesky": BlueskyConnector(),
            "telegram": TelegramConnector(),
            "facebook": FacebookConnector(),
            "linkedin": LinkedInConnector(),
        }

    async def dispatch(self, post_data: PostCreate) -> List[PostResult]:
        tasks = []

        for platform in post_data.platforms:
            platform_lower = platform.lower()
            if platform_lower in self.connectors:
                connector = self.connectors[platform_lower]
                tasks.append(connector.post(post_data.content, post_data.media_urls))

        if not tasks:
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for res in results:
            if isinstance(res, Exception):
                final_results.append(PostResult(
                    platform="unknown",
                    success=False,
                    error_message=str(res)
                ))
            else:
                final_results.append(res)

        return final_results
