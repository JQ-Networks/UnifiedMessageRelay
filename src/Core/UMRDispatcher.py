from typing import Union, List, DefaultDict, Tuple, Any
import asyncio
from collections import defaultdict
from janus import Queue
from .UMRType import UnifiedMessage, ForwardAction, ForwardActionType, SendAction, DestinationMessageID
from . import UMRLogging
from .UMRDriver import api_lookup, api_call
from .UMRConfig import config
from .UMRMessageRelation import set_message_id, get_message_id
from .UMRMessageHook import message_hook_src, message_hook_full
from Util.Helper import check_attribute
from copy import deepcopy

logger = UMRLogging.getLogger('Dispatcher')

attributes = [
    'Accounts',
    'Topology'
]

check_attribute(config['ForwardList'], attributes, logger)
# bot accounts for each platform
bot_accounts = config['ForwardList']['Accounts']

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
    if message.chat_attrs.chat_id not in action_graph[message.chat_attrs.platform]:
        logger.debug(
            f'ignoring unrelated message from {message.chat_attrs.platform}: {message.chat_attrs.chat_id}')

    # hook for matching source only
    for hook in message_hook_src:
        if (not hook.src_driver or message.chat_attrs.platform in hook.src_driver) and \
                (not hook.src_chat or message.chat_attrs.chat_id in hook.src_chat):
            if await hook.hook_function(message):
                return

    message_id_list: List[DestinationMessageID] = list()  # list of List[platform, chat_id, message_id]

    for action in action_graph[message.chat_attrs.platform][message.chat_attrs.chat_id]:

        # hook for matching all four attributes
        for hook in message_hook_full:
            if (not hook.src_driver or message.chat_attrs.platform in hook.src_driver) and \
                    (not hook.src_chat or message.chat_attrs.chat_id in hook.src_chat) and \
                    (not hook.dst_driver or action.to_platform in hook.dst_driver) and \
                    (not hook.dst_chat or action.to_chat in hook.dst_chat):
                if hook.hook_function(action.to_platform, action.to_chat, message):
                    continue

        # basic message filtering
        if action.action_type == ForwardActionType.Reply and not message.chat_attrs.reply_to:
            continue

        # check api registration
        if not api_lookup(action.to_platform, 'send'):
            continue

        if message.chat_attrs.reply_to:
            reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                              src_chat_id=message.chat_attrs.chat_id,
                                              message_id=message.chat_attrs.reply_to.message_id,
                                              dst_platform=action.to_platform,
                                              dst_chat_id=action.to_chat)

            # reply to real user on the other side
            if reply_message_id:
                message.send_action = SendAction(message_id=reply_message_id.message_id,
                                                 user_id=reply_message_id.user_id)

            # filter duplicate reply (the fact that user is actually replying to bot)
            reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                              src_chat_id=message.chat_attrs.chat_id,
                                              message_id=message.chat_attrs.reply_to.message_id,
                                              dst_platform=message.chat_attrs.platform,
                                              dst_chat_id=message.chat_attrs.chat_id)

            if reply_message_id and reply_message_id.user_id == bot_accounts[message.chat_attrs.platform]:
                message.chat_attrs.reply_to = None

        message_id = await api_call(action.to_platform, 'send', action.to_chat, message)
        if action.to_platform == message.chat_attrs.platform:
            user_id = message.chat_attrs.user_id
        else:
            user_id = bot_accounts[action.to_platform]
        message_id_list.append(
            DestinationMessageID(platform=action.to_platform,
                                 chat_id=action.to_chat,
                                 message_id=message_id,
                                 user_id=user_id)
        )

        logger.debug(f'added new task to ({action.to_platform}, {action.to_chat})')

    for idx in range(len(message_id_list)):
        if isinstance(message_id_list[idx], int):
            continue
        else:
            message_id_list[idx].message_id = message_id_list[idx].message_id.result()

    message_id_list.append(DestinationMessageID(platform=message.chat_attrs.platform,
                                                chat_id=message.chat_attrs.chat_id,
                                                message_id=message.chat_attrs.message_id,
                                                user_id=message.chat_attrs.user_id))
    set_message_id(message_id_list)
