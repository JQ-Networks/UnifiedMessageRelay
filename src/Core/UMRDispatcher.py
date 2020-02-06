from typing import Union, List, DefaultDict, Tuple, Any
import asyncio
from collections import defaultdict
from janus import Queue
import concurrent.futures
from .UMRType import UnifiedMessage, ForwardAction, ForwardActionType, SendAction, DestinationMessageID
from . import UMRLogging
from .UMRDriver import api_lookup, api_call
from .UMRConfig import config
from .UMRMessageRelation import set_message_id, get_message_id, get_relation_dict
from .UMRMessageHook import message_hook_src, message_hook_full
from Util.Helper import check_attribute
from .UMRFile import get_image

logger = UMRLogging.getLogger('Dispatcher')

attributes = [
    'Accounts',
    'Topology',
    'Default'
]

check_attribute(config['ForwardList'], attributes, logger)
# bot accounts for each platform
bot_accounts = config['ForwardList']['Accounts']

# forward graph

action_graph: DefaultDict[str, DefaultDict[int, List[ForwardAction]]] = defaultdict(
    lambda: defaultdict(lambda: list()))  # action graph

default_action_graph: DefaultDict[str, List[ForwardAction]] = defaultdict(list)

attributes = [
    'From',
    'FromChat',
    'To',
    'ToChat',
    'ForwardType'
]

# initialize action_graph
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

# initialize default_action_graph
for i in config['ForwardList']['Default']:
    default_action_graph[i['From']].append(ForwardAction(i['To'], i['ToChat'], ForwardActionType.Reply))


##### core dispatcher #####

async def dispatch_reply(message: UnifiedMessage):
    """
    dispatch messages that replied messages forwarded by default rule
    :param message:
    :return:
    """
    message_id_list: List[DestinationMessageID] = list()  # list of List[platform, chat_id, message_id]

    # check reply
    if message.chat_attrs.reply_to:
        # reply to bot, and action is not defined
        if message.chat_attrs.reply_to.user_id == bot_accounts[message.chat_attrs.platform]:
            reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                              src_chat_id=message.chat_attrs.chat_id,
                                              message_id=message.chat_attrs.reply_to.message_id,
                                              dst_platform=message.chat_attrs.platform,
                                              dst_chat_id=message.chat_attrs.chat_id)
            if not reply_message_id or not reply_message_id.source:
                return False

            # from same chat, ignore
            if reply_message_id.source.platform == message.chat_attrs.platform and \
                    reply_message_id.source.chat_id == message.chat_attrs.chat_id:
                return False

            # action is defined, ignore
            if action_graph[reply_message_id.source.platform][reply_message_id.source.chat_id]:
                return False

            source_message_id = DestinationMessageID(platform=message.chat_attrs.platform,
                                                     chat_id=message.chat_attrs.chat_id,
                                                     message_id=message.chat_attrs.message_id,
                                                     user_id=message.chat_attrs.user_id)

            message.chat_attrs.reply_to = None
            message.send_action = SendAction(message_id=reply_message_id.source.message_id,
                                             user_id=reply_message_id.source.user_id)
            if message.image.startswith('http'):
                message.image = await get_image(message.image, message.file_id)
            message_id = await api_call(reply_message_id.source.platform, 'send',
                                        reply_message_id.source.chat_id, message)
            message_id_list.append(
                DestinationMessageID(platform=reply_message_id.source.platform,
                                     chat_id=reply_message_id.source.chat_id,
                                     message_id=message_id,
                                     user_id=reply_message_id.source.user_id,
                                     source=source_message_id)
            )

            for idx in range(len(message_id_list)):
                if isinstance(message_id_list[idx], int):
                    continue
                else:
                    message_id_list[idx].message_id = message_id_list[idx].message_id.result()

            message_id_list.append(source_message_id)
            set_message_id(message_id_list)
            return True
    return False


async def dispatch_default(message: UnifiedMessage):
    message_id_list: List[DestinationMessageID] = list()  # list of List[platform, chat_id, message_id]

    # has other match
    if action_graph[message.chat_attrs.platform][message.chat_attrs.chat_id]:
        return False

    # no other rule could be matched, finish early
    if not default_action_graph[message.chat_attrs.platform]:
        return True

    source_message_id = DestinationMessageID(platform=message.chat_attrs.platform,
                                             chat_id=message.chat_attrs.chat_id,
                                             message_id=message.chat_attrs.message_id,
                                             user_id=message.chat_attrs.user_id)

    # default forward
    for action in default_action_graph[message.chat_attrs.platform]:
        if message.image.startswith('http'):
            message.image = await get_image(message.image, message.file_id)
        message_id = await api_call(action.to_platform, 'send', action.to_chat, message)
        if action.to_platform == message.chat_attrs.platform:
            user_id = message.chat_attrs.user_id
        else:
            user_id = bot_accounts[action.to_platform]
        message_id_list.append(
            DestinationMessageID(platform=action.to_platform,
                                 chat_id=action.to_chat,
                                 message_id=message_id,
                                 user_id=user_id,
                                 source=source_message_id)
        )

    for idx in range(len(message_id_list)):
        if isinstance(message_id_list[idx], int):
            continue
        else:
            message_id_list[idx].message_id = message_id_list[idx].message_id.result()

    message_id_list.append(source_message_id)
    set_message_id(message_id_list)
    return True


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

    # check reply
    if await dispatch_reply(message):
        return

    # check default
    if await dispatch_default(message):
        return

    message_id_list: List[DestinationMessageID] = list()  # list of List[platform, chat_id, message_id]

    source_message_id = DestinationMessageID(platform=message.chat_attrs.platform,
                                             chat_id=message.chat_attrs.chat_id,
                                             message_id=message.chat_attrs.message_id,
                                             user_id=message.chat_attrs.user_id)

    for action in action_graph[message.chat_attrs.platform][message.chat_attrs.chat_id]:

        # hook for matching all four attributes
        for hook in message_hook_full:
            if (not hook.src_driver or message.chat_attrs.platform in hook.src_driver) and \
                    (not hook.src_chat or message.chat_attrs.chat_id in hook.src_chat) and \
                    (not hook.dst_driver or action.to_platform in hook.dst_driver) and \
                    (not hook.dst_chat or action.to_chat in hook.dst_chat):
                if hook.hook_function(action.to_platform, action.to_chat, message):
                    continue

        # check api registration
        if not api_lookup(action.to_platform, 'send'):
            continue

        if action.action_type == ForwardActionType.Reply:
            if message.chat_attrs.reply_to:
                reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                                  src_chat_id=message.chat_attrs.chat_id,
                                                  message_id=message.chat_attrs.reply_to.message_id,
                                                  dst_platform=action.to_platform,
                                                  dst_chat_id=action.to_chat)
                if not reply_message_id:
                    continue
                if (message.chat_attrs.platform == message.chat_attrs.reply_to.platform
                        and message.chat_attrs.chat_id == message.chat_attrs.reply_to.chat_id
                        and message.chat_attrs.reply_to.user_id != bot_accounts[message.chat_attrs.platform]):
                    continue
            else:
                continue

        if message.chat_attrs.reply_to:
            reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                              src_chat_id=message.chat_attrs.chat_id,
                                              message_id=message.chat_attrs.reply_to.message_id,
                                              dst_platform=action.to_platform,
                                              dst_chat_id=action.to_chat)

            # filter duplicate reply (the fact that user is actually replying to bot)
            if message.chat_attrs.reply_to.user_id == bot_accounts[message.chat_attrs.platform]:
                message.chat_attrs.reply_to = None
                # reply to real user on the other side
                if reply_message_id:
                    # basic message filtering
                    message.send_action = SendAction(message_id=reply_message_id.message_id,
                                                     user_id=reply_message_id.user_id)
        if message.image.startswith('http'):
            message.image = await get_image(message.image, message.file_id)
        message_id = await api_call(action.to_platform, 'send', action.to_chat, message)
        if action.to_platform == message.chat_attrs.platform:
            user_id = message.chat_attrs.user_id
        else:
            user_id = bot_accounts[action.to_platform]
        message_id_list.append(
            DestinationMessageID(platform=action.to_platform,
                                 chat_id=action.to_chat,
                                 message_id=message_id,
                                 user_id=user_id,
                                 source=source_message_id)
        )

        logger.debug(f'added new task to ({action.to_platform}, {action.to_chat})')

    for idx in range(len(message_id_list)):
        if isinstance(message_id_list[idx], int):
            continue
        else:
            try:
                message_id_list[idx].message_id = message_id_list[idx].message_id.result(timeout=30)
            except concurrent.futures.TimeoutError:
                logger.warn(f'task ({message_id_list[idx].platform}, {message_id_list[idx].chat_id})'
                            f' took longer than 30 seconds, aborting')
                message_id_list[idx].message_id.interrupt()
                message_id_list[idx].message_id = 0

    message_id_list.append(source_message_id)
    message_id_list = [*filter(lambda x: x.message_id > 0, message_id_list)]
    set_message_id(message_id_list)
