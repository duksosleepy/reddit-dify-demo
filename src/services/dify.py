"""
Dify service for processing messages using the Dify API.
"""

import logging
from typing import Optional

from dify_client import Dify

logger = logging.getLogger(__name__)


class DifyService:
    """Service for interacting with the Dify API."""

    def __init__(
        self, api_key: str, endpoint: str, app_id: Optional[str] = None
    ):
        """Initialize the Dify service.

        Args:
            api_key: Dify API key
            endpoint: Dify API endpoint
            app_id: Optional Dify application ID
        """
        self.client = Dify(api_key=api_key, endpoint=endpoint, app_id=app_id)
        logger.info(f"Initialized Dify client with endpoint: {endpoint}")

    def process_message(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        response_mode: str = "blocking",
    ) -> Optional[str]:
        """Process a message through Dify and return the response.

        Args:
            user_id: User identifier (e.g., Reddit username)
            message: Message content to process
            conversation_id: Optional conversation ID for continuing a conversation
            response_mode: Dify response mode ("blocking" or "streaming")

        Returns:
            Response text from Dify or None if processing failed
        """
        try:
            logger.info(f"Processing message from {user_id} with Dify")

            # Prepare parameters
            params = {
                "user_id": user_id,
                "inputs": {},  # Additional input parameters if needed
                "query": message,
                "response_mode": response_mode,
            }

            # Add conversation_id if provided
            if conversation_id:
                params["conversation_id"] = conversation_id

            # Send request to Dify
            response = self.client.chat_message(**params)

            # Extract the answer from the response
            if response and "answer" in response:
                return response["answer"]

            # Handle streaming response
            if response_mode == "streaming":
                answer = ""
                for chunk in response:
                    if chunk and chunk.get("answer"):
                        answer += chunk["answer"]
                return answer

            logger.warning(f"Unexpected response format: {response}")
            return None

        except Exception as e:
            logger.error(
                f"Error processing message with Dify: {e}", exc_info=True
            )
            return None

    def create_conversation(self, user_id: str) -> Optional[str]:
        """Create a new conversation in Dify.

        Args:
            user_id: User identifier

        Returns:
            Conversation ID or None if creation failed
        """
        try:
            response = self.client.create_conversation(user_id=user_id)
            if response and "conversation_id" in response:
                return response["conversation_id"]
            return None
        except Exception as e:
            logger.error(f"Error creating conversation: {e}", exc_info=True)
            return None
