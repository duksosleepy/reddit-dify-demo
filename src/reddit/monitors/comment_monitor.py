"""
Monitor for Reddit comments in a subreddit.
"""

import logging
import time
from typing import Callable

from src.reddit.client import RedditBaseClient

logger = logging.getLogger(__name__)


class CommentMonitor:
    """Monitor for Reddit comments in a subreddit."""

    def __init__(self, base_client: RedditBaseClient):
        """Initialize the comment monitor.

        Args:
            base_client: Authenticated Reddit base client
        """
        self.reddit = base_client.get_reddit_instance()
        self.username = base_client.get_username()

    def start_monitoring(
        self,
        subreddit_name: str,
        callback: Callable[[str, str, str], None],
        interval: int = 30,
    ):
        """Start monitoring comments in a subreddit.

        Args:
            subreddit_name: Name of the subreddit to monitor
            callback: Function to call with (comment_id, author, comment_body)
            interval: Seconds to wait between checks
        """
        logger.info(f"Starting comment monitoring for r/{subreddit_name}")
        subreddit = self.reddit.subreddit(subreddit_name)

        while True:
            try:
                for comment in subreddit.comments(limit=100):
                    # Skip comments by the bot itself
                    if comment.author and comment.author.name == self.username:
                        continue

                    # Process recent comments (within last interval)
                    comment_age = time.time() - comment.created_utc
                    if comment_age < interval:
                        author = (
                            comment.author.name if comment.author else "Unknown"
                        )
                        logger.info(
                            f"Processing comment from {author} in r/{subreddit_name}"
                        )
                        callback(comment.fullname, author, comment.body)

                time.sleep(interval)

            except Exception as e:
                logger.error(
                    f"Error monitoring r/{subreddit_name}: {e}", exc_info=True
                )
                time.sleep(interval)  # Continue despite errors
