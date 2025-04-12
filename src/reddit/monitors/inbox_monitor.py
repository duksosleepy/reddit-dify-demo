"""
Monitor for Reddit inbox messages.
"""

import logging
import time
from typing import Callable

from src.reddit.client import RedditBaseClient

logger = logging.getLogger(__name__)


class InboxMonitor:
    """Monitor for Reddit inbox messages."""

    def __init__(self, base_client: RedditBaseClient):
        """Initialize the inbox monitor.

        Args:
            base_client: Authenticated Reddit base client
        """
        self.reddit = base_client.get_reddit_instance()
        self.username = base_client.get_username()

    def start_monitoring(
        self, callback: Callable[[str, str, str], None], interval: int = 30
    ):
        """Start monitoring the inbox for new messages.

        Args:
            callback: Function to call with (message_id, author, message_body)
            interval: Seconds to wait between checks
        """
        logger.info("Starting inbox monitoring")

        while True:
            try:
                # Check for new messages
                for item in self.reddit.inbox.unread(limit=25):
                    # Skip messages from the bot itself
                    if item.author and item.author.name == self.username:
                        item.mark_read()
                        continue

                    author = item.author.name if item.author else "Unknown"

                    # Process the message
                    logger.info(f"Processing message from {author}")
                    callback(item.fullname, author, item.body)

                    # Mark as read
                    item.mark_read()

                time.sleep(interval)

            except Exception as e:
                logger.error(f"Error monitoring inbox: {e}", exc_info=True)
                time.sleep(interval)  # Continue despite errors
