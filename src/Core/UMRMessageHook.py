from typing import List, Callable, Union
from .UMRType import MessageHook
from . import UMRLogging

logger = UMRLogging.getLogger('MessageHook')

message_hook_full: List[MessageHook] = list()  # src_driver, src_group, dst_driver, dst_group, hook
message_hook_src: List[MessageHook] = list()


def register_hook(src_driver: Union[str, List[str]] = '', src_chat: Union[int, List[int]] = 0,
                  dst_driver: Union[str, List[str]] = '', dst_chat: Union[int, List[int]] = 0) -> Callable:
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
            message_hook_src.append(MessageHook(src_driver, src_chat, dst_driver, dst_chat, original_func))
        else:
            message_hook_full.append(MessageHook(src_driver, src_chat, dst_driver, dst_chat, original_func))
        return original_func

    return deco

# There are two types of hook definitions, see MessageHook.md
