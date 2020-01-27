from collections import OrderedDict
from typing import List, Tuple, Union
from . import UMRLogging
from .UMRType import GroupID, MessageID, DestinationMessageID

logger = UMRLogging.getLogger('MessageRelation')


class FIFODict(OrderedDict):
    def __init__(self, capacity):
        super().__init__()
        self._capacity = capacity  # cache size

    def __setitem__(self, key, value):
        contains_key = key in self
        if len(self) - int(contains_key) >= self._capacity:
            self.popitem(last=False)  # pop the first element if full
        OrderedDict.__setitem__(self, key, value)


message_mapping = FIFODict(4096)  # at least twice as large as message_tuple


def set_message_id(message_id_list: List[DestinationMessageID]):
    """
    put a list of [platform, chat_id, user_id, message_id] into mapping
    the reason why user_id is needed: if the platform doesn't support reply, the reply can fallback to mention the user
    :param message_id_list: list of [platform, chat_id, user_id, message_id]
    :return: None
    """
    saved_mapping = {GroupID(platform=i.platform, chat_id=i.chat_id): i for i in message_id_list}
    for i in message_id_list:
        message_mapping[MessageID(platform=i.platform, chat_id=i.chat_id, message_id=i.message_id)] = saved_mapping


def get_message_id(src_platform: str, src_chat_id: int, message_id: int, dst_platform: str, dst_chat_id: int) \
        -> DestinationMessageID:
    """

    :param src_platform:
    :param src_chat_id:
    :param message_id:
    :param dst_platform:
    :param dst_chat_id:
    :return: tuple of user_id, message_id
    """
    return message_mapping.get(MessageID(platform=src_platform, chat_id=src_chat_id, message_id=message_id),
                               dict()).get(GroupID(platform=dst_platform, chat_id=dst_chat_id))
