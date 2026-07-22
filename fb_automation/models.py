"""
Data models for Facebook automation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(slots=True)
class FacebookPost:
    """
    Represents a scraped Facebook post.
    """

    author: str
    text: str
    timestamp: str = ""

    post_url: str = ""

    images: List[str] = field(default_factory=list)

    links: List[str] = field(default_factory=list)

    commented: bool = False

    comment_text: str = ""

    comment_time: str = ""

    scraped_at: str = field(
        default_factory=lambda: datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    def mark_commented(
        self,
        comment: str,
    ) -> None:
        """
        Mark the post as commented.
        """

        self.commented = True

        self.comment_text = comment

        self.comment_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def fingerprint(self) -> str:
        """
        Generate a fingerprint used for duplicate detection.
        """

        return (
            f"{self.author}|"
            f"{self.text[:250]}"
        )

    def to_dict(self) -> dict:
        """
        Convert model to serializable dictionary.
        """

        return {
            "author": self.author,
            "text": self.text,
            "timestamp": self.timestamp,
            "post_url": self.post_url,
            "images": self.images,
            "links": self.links,
            "commented": self.commented,
            "comment_text": self.comment_text,
            "comment_time": self.comment_time,
            "scraped_at": self.scraped_at,
        }