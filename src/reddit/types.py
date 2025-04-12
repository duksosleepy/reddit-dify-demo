"""
Types and constants for the Reddit client.
"""

from enum import Enum, auto
from typing import Callable, TypedDict

# Type aliases
MessageCallback = Callable[[str, str, str], None]  # (item_id, author, content)


class ItemType(Enum):
    """Types of Reddit items."""

    COMMENT = auto()
    MESSAGE = auto()
    POST = auto()

    @classmethod
    def from_fullname(cls, fullname: str) -> "ItemType":
        """Get the item type from a Reddit fullname.

        Args:
            fullname: Reddit fullname (e.g., t1_abc123, t4_def456)

        Returns:
            ItemType
        """
        prefix = fullname.split("_")[0]
        if prefix == "t1":
            return cls.COMMENT
        elif prefix == "t3":
            return cls.POST
        elif prefix == "t4":
            return cls.MESSAGE
        else:
            raise ValueError(f"Unknown item type: {prefix}")


class RedditConfig(TypedDict):
    """Configuration for Reddit client."""

    client_id: str
    client_secret: str
    user_agent: str
    username: str
    password: str
