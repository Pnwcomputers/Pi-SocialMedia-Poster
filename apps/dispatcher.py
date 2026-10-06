import asyncio
from .schemas import PostCreate, PostResult
from .connectors.mastodon import MastodonConnector
from .connectors.bluesky import BlueskyConnector
# Import other connectors as they are built...

class PostDispatcher:
    def __init__(self):
        # Initialize available connectors
        self.connectors = {
            "mastodon": MastodonConnector(),
            "bluesky": BlueskyConnector(),
            # "telegram": TelegramConnector(),
            # "linkedin": LinkedInConnector(),
            # "facebook": FacebookConnector(),
        }

    async def dispatch(self, post_data: PostCreate) -> List[PostResult]:
        tasks = []
        
        for platform in post_data.platforms:
            platform_lower = platform.lower()
            if platform_lower in self.connectors:
                connector = self.connectors[platform_lower]
                # Formatters would ideally be called here before posting
                tasks.append(connector.post(post_data.content, post_data.media_urls))
            else:
                # Handle unsupported platforms
                pass
                
        # Execute all posts concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Clean up results
        final_results = []
        for res in results:
            if isinstance(res, Exception):
                # Handle unexpected thread errors
                pass
            else:
                final_results.append(res)
                
        return final_results
