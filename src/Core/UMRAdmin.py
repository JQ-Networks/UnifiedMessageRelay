from typing import Dict, List
from . import UMRConfig
from . import UMRLogging

logger = UMRLogging.getLogger('Admin')

bot_admin: Dict[str, List[int]] = UMRConfig.config['BotAdmin']


def is_bot_admin(platform: str, user_id: int) -> bool:
    """
    check if user is in bot admin list
    :param platform:
    :param user_id:
    :return:
    """
    if platform not in bot_admin:
        return False
    return user_id in bot_admin[platform]
