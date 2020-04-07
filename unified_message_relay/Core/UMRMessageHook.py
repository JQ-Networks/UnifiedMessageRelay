from typing import List, Callable, Union
from .UMRType import MessageHook, ChatType, UnifiedMessage
from . import UMRLogging

logger = UMRLogging.get_logger('MessageHook')

message_hook_full: List[MessageHook] = list()  # src_driver, src_group, dst_driver, dst_group, hook
message_hook_src: List[MessageHook] = list()


def register_hook(src_driver: Union[str, List[str]] = '', src_chat: Union[int, str, List[Union[int, str]]] = 0,
                  src_chat_type: Union[ChatType, List[ChatType]] = ChatType.UNSPECIFIED,
                  dst_driver: Union[str, List[str]] = '', dst_chat: Union[int, str, List[Union[int, str]]] = 0,
                  dst_chat_type: Union[ChatType, List[ChatType]] = ChatType.UNSPECIFIED) -> Callable:
    """
    message hook registration

    :param src_driver: driver name, not the name of platform that is specified in config.yaml
    :param src_chat: chat id
    :param src_chat_type: chat type
    :param dst_driver: driver name
    :param dst_chat: chat id
    :param dst_chat_type: chat type
    :return: decorator
    """

    def deco(original_func):
        if not dst_chat and not dst_driver:
            message_hook_src.append(MessageHook(src_driver, src_chat, src_chat_type, dst_driver, dst_chat, dst_chat_type, original_func))
        else:
            message_hook_full.append(MessageHook(src_driver, src_chat, src_chat_type, dst_driver, dst_chat, dst_chat_type, original_func))
        return original_func

    return deco


async def dispatch_hook(message: UnifiedMessage,
                        dst_driver: Union[str, List[str]] = '', dst_chat: Union[int, str, List[Union[int, str]]] = 0,
                        dst_chat_type: Union[ChatType, List[ChatType]] = ChatType.UNSPECIFIED):

    if not dst_driver and not dst_chat and dst_chat_type == ChatType.UNSPECIFIED:
        # hook for matching source only
        for hook in message_hook_src:
            if (not hook.src_driver or message.chat_attrs.platform in hook.src_driver) and \
                    (ChatType.UNSPECIFIED in hook.src_chat_type or message.chat_attrs.chat_type in hook.src_chat_type) and \
                    (not hook.src_chat or message.chat_attrs.chat_id in hook.src_chat):
                if await hook.hook_function(message):
                    return True
    else:
        # hook for matching all four attributes
        for hook in message_hook_full:
            if (not hook.src_driver or message.chat_attrs.platform in hook.src_driver) and \
                    (not hook.src_chat or message.chat_attrs.chat_id in hook.src_chat) and \
                    (ChatType.UNSPECIFIED in hook.src_chat_type or message.chat_attrs.chat_type in hook.src_chat_type) and \
                    (not hook.dst_driver or dst_driver in hook.dst_driver) and \
                    (ChatType.UNSPECIFIED in hook.dst_chat_type or dst_chat_type in hook.src_chat_type) and \
                    (not hook.dst_chat or dst_chat in hook.dst_chat):
                if await hook.hook_function(dst_driver, dst_chat, dst_chat_type, message):
                    return True

    return False

# There are two types of hook definitions, see MessageHook.md
