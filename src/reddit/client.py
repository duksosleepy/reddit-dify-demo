"""
Base Reddit client for authentication and common functionality.
"""

import logging

import praw

logger = logging.getLogger(__name__)


class RedditBaseClient:
    """Base client for interacting with Reddit API using PRAW."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        username: str,
        password: str,
    ):
        """Initialize the Reddit client with authentication.

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string (format: <platform>:<app name>:<version> by <username>)
            username: Reddit username
            password: Reddit password
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password,
        )
        self.username = username

        # Verify authentication
        self._verify_authentication()

    def _verify_authentication(self):
        """Verify that authentication was successful."""
        try:
            user = self.reddit.user.me()
            logger.info(f"Successfully authenticated as {self.username}")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}", exc_info=True)
            raise RuntimeError("Failed to authenticate with Reddit") from e

    def get_reddit_instance(self) -> praw.Reddit:
        """Get the authenticated Reddit instance.

        Returns:
            Authenticated PRAW Reddit instance
        """
        return self.reddit

    def get_username(self) -> str:
        """Get the authenticated username.

        Returns:
            Username of the authenticated account
        """
        return self.username
