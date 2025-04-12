"""
Main entry point for the Reddit-Dify integration bot.
"""

import argparse
import logging
import os
import sys
from typing import Dict

from src.reddit.client import RedditBaseClient
from src.reddit.monitors.comment_monitor import CommentMonitor
from src.reddit.monitors.inbox_monitor import InboxMonitor
from src.reddit.responders.message_responder import MessageResponder
from src.services.dify import DifyService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log"),
    ],
)
logger = logging.getLogger(__name__)

# Dictionary to store active conversations
conversations: Dict[str, str] = {}


def load_environment_variables() -> Dict[str, str]:
    """Load and validate required environment variables.

    Returns:
        Dictionary of environment variables

    Raises:
        ValueError: If any required variables are missing
    """
    required_vars = {
        "REDDIT_CLIENT_ID": os.environ.get("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": os.environ.get("REDDIT_CLIENT_SECRET"),
        "REDDIT_USERNAME": os.environ.get("REDDIT_USERNAME"),
        "REDDIT_PASSWORD": os.environ.get("REDDIT_PASSWORD"),
        "REDDIT_USER_AGENT": os.environ.get(
            "REDDIT_USER_AGENT",
            f"python:reddit-dify-demo:0.1.0 by {os.environ.get('REDDIT_USERNAME')}",
        ),
        "DIFY_API_KEY": os.environ.get("DIFY_API_KEY"),
        "DIFY_ENDPOINT": os.environ.get("DIFY_ENDPOINT"),
        "DIFY_APP_ID": os.environ.get("DIFY_APP_ID", ""),  # Optional
    }

    # Check for missing variables
    missing_vars = [
        var
        for var, value in required_vars.items()
        if var != "DIFY_APP_ID" and not value
    ]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    return required_vars


def main():
    """Main entry point for the bot."""
    parser = argparse.ArgumentParser(description="Reddit-Dify integration bot")
    parser.add_argument(
        "--mode",
        choices=["inbox", "subreddit"],
        default="inbox",
        help="Monitoring mode: inbox (messages) or subreddit (comments)",
    )
    parser.add_argument(
        "--subreddit",
        help="Subreddit to monitor (required if mode is 'subreddit')",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval in seconds between checks",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.mode == "subreddit" and not args.subreddit:
        parser.error("--subreddit is required when mode is 'subreddit'")

    try:
        # Load environment variables
        env_vars = load_environment_variables()

        # Create Reddit base client
        base_client = RedditBaseClient(
            client_id=env_vars["REDDIT_CLIENT_ID"],
            client_secret=env_vars["REDDIT_CLIENT_SECRET"],
            user_agent=env_vars["REDDIT_USER_AGENT"],
            username=env_vars["REDDIT_USERNAME"],
            password=env_vars["REDDIT_PASSWORD"],
        )

        # Create the message responder
        responder = MessageResponder(base_client)

        # Initialize Dify service
        dify_service = DifyService(
            api_key=env_vars["DIFY_API_KEY"],
            endpoint=env_vars["DIFY_ENDPOINT"],
            app_id=env_vars["DIFY_APP_ID"] if env_vars["DIFY_APP_ID"] else None,
        )

        # Create message processing callback
        def process_message(item_id: str, author: str, content: str):
            # Get or create a conversation ID for this user
            conversation_id = conversations.get(author)
            if not conversation_id:
                conversation_id = dify_service.create_conversation(
                    user_id=author
                )
                if conversation_id:
                    conversations[author] = conversation_id

            # Process the message with Dify
            response = dify_service.process_message(
                user_id=author, message=content, conversation_id=conversation_id
            )

            # Send the response back to Reddit
            if response:
                logger.info(f"Sending response to {author}")
                responder.reply_to_item(item_id, response)
            else:
                logger.warning(
                    f"No response generated for message from {author}"
                )
                # Optional: Send a fallback message
                responder.reply_to_item(
                    item_id,
                    "Sorry, I couldn't process your message at this time.",
                )

        # Start monitoring based on selected mode
        logger.info(f"Starting bot in {args.mode} mode")

        if args.mode == "inbox":
            # Create and start inbox monitor
            inbox_monitor = InboxMonitor(base_client)
            inbox_monitor.start_monitoring(
                callback=process_message, interval=args.interval
            )
        else:  # subreddit mode
            # Create and start comment monitor
            comment_monitor = CommentMonitor(base_client)
            comment_monitor.start_monitoring(
                subreddit_name=args.subreddit,
                callback=process_message,
                interval=args.interval,
            )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
