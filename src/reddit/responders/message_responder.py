"""
Responder for sending messages back to Reddit.
"""

import logging

from src.reddit.client import RedditBaseClient

logger = logging.getLogger(__name__)


class MessageResponder:
    """Responder for sending messages back to Reddit."""

    def __init__(self, base_client: RedditBaseClient):
        """Initialize the message responder.

        Args:
            base_client: Authenticated Reddit base client
        """
        self.reddit = base_client.get_reddit_instance()

    def reply_to_item(self, item_id: str, reply_text: str) -> bool:
        """Reply to a message or comment.

        Args:
            item_id: Reddit ID of the message/comment to reply to
            reply_text: Text to send as a reply

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the item by ID
            item = (
                self.reddit.inbox.message(item_id)
                if item_id.startswith("t4_")
                else self.reddit.comment(item_id)
            )

            # Send the reply
            item.reply(reply_text)
            logger.info(f"Successfully replied to {item_id}")
            return True

        except Exception as e:
            logger.error(f"Error replying to {item_id}: {e}", exc_info=True)
            return False

    def send_private_message(
        self, username: str, subject: str, message: str
    ) -> bool:
        """Send a private message to a user.

        Args:
            username: Username of the recipient
            subject: Subject line of the message
            message: Message content

        Returns:
            True if successful, False otherwise
        """
        try:
            self.reddit.redditor(username).message(subject, message)
            logger.info(f"Successfully sent private message to {username}")
            return True
        except Exception as e:
            logger.error(
                f"Error sending message to {username}: {e}", exc_info=True
            )
            return False
