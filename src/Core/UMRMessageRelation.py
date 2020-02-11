from collections import OrderedDict
from typing import List, Dict, Union
from . import UMRLogging
from .UMRType import GroupID, MessageID, DestinationMessageID, ChatType

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


def set_ingress_message_id(src_platform: str, src_chat_id: Union[int, str], src_chat_type: ChatType, src_message_id: int, user_id):
    """
    Register related message id (for message received by bot)
    :param src_chat_type:
    :param src_platform:
    :param src_chat_id:
    :param src_message_id:
    :param user_id:
    :return:
    """
    saved_msg_id = {GroupID(platform=src_platform, chat_id=src_chat_id, chat_type=src_chat_type): DestinationMessageID(
        platform=src_platform,
        chat_id=src_chat_id,
        chat_type=src_chat_type,
        message_id=src_message_id,
        user_id=user_id)}
    message_mapping[MessageID(platform=src_platform, chat_id=src_chat_id, chat_type=src_chat_type, message_id=src_message_id)] = saved_msg_id


def set_egress_message_id(src_platform: str, src_chat_id: Union[int, str], src_message_id: Union[int, str], src_chat_type: ChatType,
                          dst_platform: str, dst_chat_id: Union[int, str], dst_message_id: int, dst_chat_type: ChatType, user_id: int):
    """
    Register related message id (for message sent by bot)
    :param src_chat_type:
    :param dst_chat_type:
    :param src_platform:
    :param src_chat_id:
    :param src_message_id:
    :param dst_platform:
    :param dst_chat_id:
    :param dst_message_id:
    :param user_id:
    :return:
    """
    saved_msg_id = message_mapping.get(MessageID(platform=src_platform,
                                       chat_id=src_chat_id, chat_type=src_chat_type, message_id=src_message_id), dict())

    if not saved_msg_id:  # message relation not found
        return

    source = saved_msg_id.get(GroupID(platform=src_platform, chat_id=src_chat_id, chat_type=src_chat_type))

    dst_msg_id = DestinationMessageID(platform=dst_platform, chat_id=dst_chat_id, chat_type=dst_chat_type,
                                      message_id=dst_message_id, user_id=user_id, source=source)
    saved_msg_id[GroupID(platform=dst_platform, chat_id=dst_chat_id, chat_type=dst_chat_type)] = dst_msg_id
    message_mapping[MessageID(platform=dst_platform, chat_id=dst_chat_id, chat_type=dst_chat_type, message_id=dst_message_id)] = saved_msg_id


def get_message_id(src_platform: str, src_chat_id: Union[int, str], src_chat_type: ChatType, src_message_id: int, dst_platform: str, dst_chat_id: Union[int, str], dst_chat_type: ChatType) \
        -> DestinationMessageID:
    """

    :param dst_chat_type:
    :param src_chat_type:
    :param src_platform:
    :param src_chat_id:
    :param src_message_id:
    :param dst_platform:
    :param dst_chat_id:
    :return: tuple of user_id, message_id
    """
    return message_mapping.get(MessageID(platform=src_platform, chat_id=src_chat_id, chat_type=src_chat_type, message_id=src_message_id),
                               dict()).get(GroupID(platform=dst_platform, chat_id=dst_chat_id, chat_type=dst_chat_type))


def get_relation_dict(src_platform: str, src_chat_id: Union[int, str], src_chat_type: ChatType, message_id: int) -> Dict[MessageID, DestinationMessageID]:
    return message_mapping.get(MessageID(platform=src_platform, chat_id=src_chat_id, chat_type=src_chat_type, message_id=message_id),
                               dict())
