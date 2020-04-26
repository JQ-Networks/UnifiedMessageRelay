from typing import Dict, List
from . import UMRConfig
from . import UMRLogging
from .UMRDriver import api_call
from .UMRType import ChatType

# Stateless

logger = UMRLogging.get_logger('Admin')


async def is_bot_admin(platform: str, user_id: int) -> bool:
    """
    check if user is in bot admin list
    :param platform:
    :param user_id:
    :return:
    """
    if platform not in UMRConfig.config.BotAdmin:
        return False
    return user_id in UMRConfig.config.BotAdmin[platform]


async def is_group_owner(platform: str, chat_id: int, chat_type: ChatType, user_id: int):
    if chat_id > 0:  # private chat
        return False
    result = await api_call(platform, 'is_group_owner', chat_id, chat_type, user_id)
    if result:  # result can be None if driver does not have is_group_owner
        if isinstance(result, bool):
            return result
        else:
            return result.result()
    else:
        return False


async def is_group_admin(platform: str, chat_id: int, chat_type: ChatType, user_id: int):
    if chat_id > 0:  # private chat
        return False
    result = await api_call(platform, 'is_group_admin', chat_id, chat_type, user_id)
    if result:  # result can be None if driver does not have is_group_admin
        if isinstance(result, bool):
            return result
        else:
            return result.result()
    else:
        return False
