from dataclasses import dataclass


@dataclass
class UnifiedMessage:
    from_platform: str
    from_chat: int
    from_user: str
    reply_to: str  # reply to some user
    message: str
    image: str
