from typing import List, Callable, Union
from .UMRType import MessageHook, ChatType
from . import UMRLogging

logger = UMRLogging.get_logger('MessageHook')

message_hook_full: List[MessageHook] = list()  # src_driver, src_group, dst_driver, dst_group, hook
message_hook_src: List[MessageHook] = list()


def register_hook(src_driver: Union[str, List[str]] = '', src_chat: Union[int, List[int]] = 0, src_chat_type: Union[ChatType, List[ChatType]] = ChatType.UNSPECIFIED,
                  dst_driver: Union[str, List[str]] = '', dst_chat: Union[int, List[int]] = 0, dst_chat_type: Union[ChatType, List[ChatType]] = ChatType.UNSPECIFIED) -> Callable:
    """
    message hook registration
    :param src_driver: driver name
    :param src_chat: chat id
    :param dst_driver: driver name
    :param dst_chat: chat id
    :return: decorator
    """

    def deco(original_func):
        if not dst_chat and not dst_driver:
            message_hook_src.append(MessageHook(src_driver, src_chat, src_chat_type, dst_driver, dst_chat, dst_chat_type, original_func))
        else:
            message_hook_full.append(MessageHook(src_driver, src_chat, src_chat_type, dst_driver, dst_chat, dst_chat_type, original_func))
        return original_func

    return deco

# There are two types of hook definitions, see MessageHook.md
