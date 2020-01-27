from typing import Union, List, DefaultDict, Tuple, Any
import asyncio
from collections import defaultdict
from janus import Queue
from .UMRType import UnifiedMessage, ForwardAction, ForwardActionType, SendAction, DestinationMessageID
from . import UMRLogging
from .UMRDriver import api_lookup
from .UMRConfig import config
from .UMRMessageRelation import set_message_id, get_message_id
from .UMRMessageHook import message_hook_src, message_hook_full
from Util.Helper import janus_queue_put_async, check_attribute
from threading import Thread

logger = UMRLogging.getLogger('Dispatcher')

# forward graph

action_graph: DefaultDict[str, DefaultDict[int, List[ForwardAction]]] = defaultdict(
    lambda: defaultdict(lambda: list()))  # action graph

attributes = [
    'From',
    'FromChat',
    'To',
    'ToChat',
    'ForwardType'
]
for i in config['ForwardList']['Topology']:
    check_attribute(i, attributes, logger)

    # Add action
    # BiDirection = two ALL
    # OneWay      = one All
    # ReplyOnly = one Reply

    # init forward graph and workers
    if i['ForwardType'] == 'BiDirection':
        action_type = ForwardActionType.All
        action_graph[i['From']][i['FromChat']].append(
            ForwardAction(i['To'], i['ToChat'], action_type))
        action_graph[i['To']][i['ToChat']].append(
            ForwardAction(i['From'], i['FromChat'], action_type))
    elif i['ForwardType'] == 'OneWay':
        action_type = ForwardActionType.All
        action_graph[i['From']][i['FromChat']].append(
            ForwardAction(i['To'], i['ToChat'], action_type))
    elif i['ForwardType'] == 'ReplyOnly':
        action_type = ForwardActionType.Reply
        action_graph[i['From']][i['FromChat']].append(
            ForwardAction(i['To'], i['ToChat'], action_type))
    else:
        logger.warning(f'Unrecognized ForwardType in config: "{i["ForwardType"]}", ignoring')


##### core dispatcher #####

async def dispatch(message: UnifiedMessage):
    if message.forward_attrs.from_chat not in action_graph[message.forward_attrs.from_platform]:
        logger.debug(
            f'ignoring unrelated message from {message.forward_attrs.from_platform}: {message.forward_attrs.from_chat}')

    # hook for matching source only
    for hook in message_hook_src:
        if (not hook.src_driver or message.forward_attrs.from_platform in hook.src_driver) and \
                (not hook.src_chat or message.forward_attrs.from_chat in hook.src_chat):
            if await hook.hook_function(message):
                return

    message_id_list: List = list()  # list of List[platform, chat_id, message_id]

    for action in action_graph[message.forward_attrs.from_platform][message.forward_attrs.from_chat]:

        # hook for matching all four attributes
        for hook in message_hook_full:
            if (not hook.src_driver or message.forward_attrs.from_platform in hook.src_driver) and \
                    (not hook.src_chat or message.forward_attrs.from_chat in hook.src_chat) and \
                    (not hook.dst_driver or action.to_platform in hook.dst_driver) and \
                    (not hook.dst_chat or action.to_chat in hook.dst_chat):
                if hook.hook_function(action.to_platform, action.to_chat, message):
                    continue

        # basic message filtering
        if action.action_type == ForwardActionType.Reply and not message.forward_attrs.reply_to_user:
            continue

        # check api registration
        api_send = api_lookup(action.to_platform, 'send')
        if not api_send:
            continue

        reply_message_id = get_message_id(src_platform=message.forward_attrs.from_platform,
                                          src_chat_id=message.forward_attrs.from_chat,
                                          message_id=message.forward_attrs.reply_to_message_id,
                                          dst_platform=action.to_platform,
                                          dst_chat_id=action.to_chat)

        if reply_message_id:
            message.send_action = SendAction(message_id=reply_message_id.message_id, user_id=reply_message_id.user_id)

        if asyncio.iscoroutinefunction(api_send):
            future = await api_send(action.to_chat, message)  # return a Future
            message_id_list.append(future)
        else:
            message_id = api_send(action.to_chat, message)
            message_id_list.append(message_id)

        for idx in range(len(message_id_list)):
            if isinstance(message_id_list[idx], int):
                message_id_list[idx] = DestinationMessageID(platform=action.to_platform,
                                                            chat_id=action.to_chat,
                                                            message_id=message_id_list[idx],
                                                            user_id=message.forward_attrs.from_user_id)
            else:
                message_id_list[idx] = DestinationMessageID(platform=action.to_platform,
                                                            chat_id=action.to_chat,
                                                            message_id=message_id_list[idx].result(),
                                                            user_id=message.forward_attrs.from_user_id)

        message_id_list.append(DestinationMessageID(platform=message.forward_attrs.from_platform,
                                                    chat_id=message.forward_attrs.from_chat,
                                                    message_id=message.forward_attrs.from_message_id,
                                                    user_id=message.forward_attrs.from_user_id))
        set_message_id(message_id_list)

        logger.debug(f'added new task to ({action.to_platform}, {action.to_chat})')
