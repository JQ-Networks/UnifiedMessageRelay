from typing import Union, List, DefaultDict, Tuple, Any, Union, Dict
import asyncio
from collections import defaultdict
from janus import Queue
from .UMRType import UnifiedMessage, ForwardAction, ForwardActionType, DefaultForwardAction, DefaultForwardActionType, SendAction, ChatType, GroupID
from . import UMRLogging
from . import UMRDriver
from .UMRConfig import config
from .UMRMessageRelation import get_message_id
from .UMRMessageHook import message_hook_src, message_hook_full
from ..Util.Helper import check_attribute
from .UMRFile import get_image


class UMRDispatcher:
    def __init__(self):
        self.logger = UMRLogging.get_logger('Dispatcher')

        # check basic config
        attributes = [
            ('Accounts', True, defaultdict(lambda: 0)),
            ('Topology', True, list()),
            ('Default', True, list())
        ]

        check_attribute(config['ForwardList'], attributes, self.logger)
        # bot accounts for each platform
        self.bot_accounts = config['ForwardList']['Accounts']

        # forward graph

        self.action_graph: DefaultDict[GroupID, List[ForwardAction]] = defaultdict(lambda: list())  # action graph

        self.default_action_graph: DefaultDict[str, Dict[GroupID, DefaultForwardAction]] = defaultdict(
            lambda: dict())  # default action graph

        attributes = [
            ('From', False, None),
            ('FromChat', False, None),
            ('FromChatType', False, None),
            ('To', False, None),
            ('ToChat', False, None),
            ('ToChatType', False, None),
            ('ForwardType', True, 'BiDirection')
        ]

        default_attributes = [
            ('From', False, None),
            ('To', False, None),
            ('ToChat', False, None),
            ('ToChatType', False, None),
            ('ForwardType', True, 'OneWay+')
        ]

        self.chat_type_map = {
            'group':   ChatType.GROUP,
            'discuss': ChatType.DISCUSS,
            'private': ChatType.PRIVATE
        }

        # initialize action_graph
        for i in config['ForwardList']['Topology']:
            check_attribute(i, attributes, self.logger)

            # Add action
            # BiDirection = two ALL
            # OneWay      = one All
            # OneWay+     = one All + one Reply

            # ForwardType.All: From one platform to another, forward all message
            # ForwardType.Reply: From one platform to another, forward only replied message

            # init forward graph and workers
            if i['ForwardType'] == 'BiDirection':
                action_type = ForwardActionType.ForwardAll
                self.action_graph[GroupID(platform=i['From'],
                                          chat_id=i['FromChat'],
                                          chat_type=self.chat_type_map[i['FromChatType']])].append(
                    ForwardAction(to_platform=i['To'],
                                  to_chat=i['ToChat'],
                                  chat_type=self.chat_type_map[i['ToChatType']],
                                  action_type=action_type))
                self.action_graph[
                    GroupID(platform=i['To'],
                            chat_id=i['ToChat'],
                            chat_type=self.chat_type_map[i['ToChatType']])].append(
                    ForwardAction(to_platform=i['From'],
                                  to_chat=i['FromChat'],
                                  chat_type=self.chat_type_map[i['FromChatType']],
                                  action_type=action_type))
            elif i['ForwardType'] in ('OneWay', 'OneWay+'):
                action_type = ForwardActionType.ForwardAll
                self.action_graph[GroupID(platform=i['From'],
                                          chat_id=i['FromChat'],
                                          chat_type=self.chat_type_map[i['FromChatType']])].append(
                    ForwardAction(to_platform=i['To'],
                                  to_chat=i['ToChat'],
                                  chat_type=self.chat_type_map[i['ToChatType']],
                                  action_type=action_type))
                if i['ForwardType'] == 'OneWay+':
                    action_type = ForwardActionType.ReplyOnly
                    self.action_graph[GroupID(platform=i['To'],
                                              chat_id=i['ToChat'],
                                              chat_type=self.chat_type_map[i['ToChatType']])].append(
                        ForwardAction(to_platform=i['From'],
                                      to_chat=i['FromChat'],
                                      chat_type=self.chat_type_map[i['FromChatType']],
                                      action_type=action_type))
            else:
                self.logger.warning(f'Unrecognized ForwardType in config: "{i["ForwardType"]}", ignoring')

        # initialize default_action_graph
        for i in config['ForwardList']['Default']:
            check_attribute(i, default_attributes, self.logger)

            # Add action
            # OneWay      = one All
            # OneWay+     = one All + one Reply

            # ForwardType.All: From one platform to another, forward all message, accept reply backward
            # ForwardType.Reply: From one platform to another, forward all message, reject reply backward

            if i['ForwardType'] == 'OneWay+':
                action_type = DefaultForwardActionType.OneWayWithReply
            elif i['ForwardType'] == 'OneWay':
                action_type = DefaultForwardActionType.OneWay
            else:
                self.logger.warning(f'Unrecognized ForwardType in config: "{i["ForwardType"]}", ignoring')
                continue
            self.default_action_graph[i['From']][
                GroupID(platform=i['To'],
                        chat_id=i['ToChat'],
                        chat_type=self.chat_type_map[i['ToChatType']])] = \
                DefaultForwardAction(to_platform=i['To'],
                                     to_chat=i['ToChat'],
                                     chat_type=self.chat_type_map[i['ToChatType']],
                                     action_type=action_type)

    async def dispatch_reply(self, message: UnifiedMessage):
        """
        dispatch messages that replied messages forwarded by default rule
        :param message:
        :return:
        """

        # check reply
        if message.chat_attrs.reply_to:
            # reply to bot, and action is not oneway
            if message.chat_attrs.reply_to.user_id == self.bot_accounts.get(message.chat_attrs.platform):
                reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                                  src_chat_id=message.chat_attrs.chat_id,
                                                  src_chat_type=message.chat_attrs.chat_type,
                                                  src_message_id=message.chat_attrs.reply_to.message_id,
                                                  dst_platform=message.chat_attrs.platform,
                                                  dst_chat_id=message.chat_attrs.chat_id,
                                                  dst_chat_type=message.chat_attrs.chat_type)
                # filter no source message (e.g. bot command)
                if not reply_message_id or not reply_message_id.source:
                    return False

                # from same chat, ignore
                if reply_message_id.source.platform == message.chat_attrs.platform and \
                        reply_message_id.source.chat_id == message.chat_attrs.chat_id:
                    return False

                # one way forward, block
                default_action = self.default_action_graph[reply_message_id.source.platform].get(
                    GroupID(platform=message.chat_attrs.platform, chat_id=message.chat_attrs.chat_id,
                            chat_type=message.chat_attrs.chat_type))
                if default_action and default_action.action_type == DefaultForwardActionType.OneWay:
                    return True

                message.chat_attrs.reply_to = None
                message.send_action = SendAction(message_id=reply_message_id.source.message_id,
                                                 user_id=reply_message_id.source.user_id)
                if message.image.startswith('http'):
                    message.image = await get_image(message.image, message.file_id)
                await UMRDriver.api_call(reply_message_id.source.platform, 'send',
                                         reply_message_id.source.chat_id, reply_message_id.source.chat_type, message)

                return True
        return False

    async def dispatch_default(self, message: UnifiedMessage):

        # action is defined, ignore
        if self.action_graph[GroupID(platform=message.chat_attrs.platform, chat_id=message.chat_attrs.chat_id,
                                     chat_type=message.chat_attrs.chat_type)]:
            return False

        # default forward
        for _, action in self.default_action_graph[message.chat_attrs.platform].items():
            if message.image.startswith('http'):
                message.image = await get_image(message.image, message.file_id)
            await UMRDriver.api_call(action.to_platform, 'send', action.to_chat, action.chat_type, message)

        if self.default_action_graph[message.chat_attrs.platform]:
            return True
        else:
            return False

    async def dispatch(self, message: UnifiedMessage):

        # hook for matching source only
        for hook in message_hook_src:
            if (not hook.src_driver or message.chat_attrs.platform in hook.src_driver) and \
                    (ChatType.UNSPECIFIED in hook.src_chat_type or message.chat_attrs.chat_type in hook.src_chat_type) and \
                    (not hook.src_chat or message.chat_attrs.chat_id in hook.src_chat):
                if await hook.hook_function(message):
                    return

        # check reply
        if await self.dispatch_reply(message):
            return

        # check default
        if await self.dispatch_default(message):
            return

        for action in self.action_graph[GroupID(platform=message.chat_attrs.platform,
                                                chat_id=message.chat_attrs.chat_id,
                                                chat_type=message.chat_attrs.chat_type)]:

            # hook for matching all four attributes
            for hook in message_hook_full:
                if (not hook.src_driver or message.chat_attrs.platform in hook.src_driver) and \
                        (not hook.src_chat or message.chat_attrs.chat_id in hook.src_chat) and \
                        (ChatType.UNSPECIFIED in hook.src_chat_type or message.chat_attrs.chat_type in hook.src_chat_type) and \
                        (not hook.dst_driver or action.to_platform in hook.dst_driver) and \
                        (ChatType.UNSPECIFIED in hook.dst_chat_type or action.chat_type in hook.src_chat_type) and \
                        (not hook.dst_chat or action.to_chat in hook.dst_chat):
                    if hook.hook_function(action.to_platform, action.to_chat, action.chat_type, message):
                        continue

            if action.action_type == ForwardActionType.ReplyOnly:
                if message.chat_attrs.reply_to:
                    reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                                      src_chat_id=message.chat_attrs.chat_id,
                                                      src_chat_type=message.chat_attrs.chat_type,
                                                      src_message_id=message.chat_attrs.reply_to.message_id,
                                                      dst_platform=action.to_platform,
                                                      dst_chat_id=action.to_chat,
                                                      dst_chat_type=action.chat_type)
                    if not reply_message_id:  # not replying to forwarded message
                        continue

                    if (message.chat_attrs.platform == message.chat_attrs.reply_to.platform  # filter same platform reply
                            and message.chat_attrs.chat_id == message.chat_attrs.reply_to.chat_id
                            and message.chat_attrs.chat_type == message.chat_attrs.chat_type
                            and message.chat_attrs.reply_to.user_id != self.bot_accounts[message.chat_attrs.platform]):
                        continue
                else:  # not a reply
                    continue

            if message.chat_attrs.reply_to:
                reply_message_id = get_message_id(src_platform=message.chat_attrs.platform,
                                                  src_chat_id=message.chat_attrs.chat_id,
                                                  src_chat_type=message.chat_attrs.chat_type,
                                                  src_message_id=message.chat_attrs.reply_to.message_id,
                                                  dst_platform=action.to_platform,
                                                  dst_chat_id=action.to_chat,
                                                  dst_chat_type=action.chat_type)

                # filter duplicate reply (the fact that user is actually replying to bot)
                if message.chat_attrs.reply_to.user_id == self.bot_accounts[message.chat_attrs.platform]:
                    message.chat_attrs.reply_to = None
                    # reply to real user on the other side
                    if reply_message_id:
                        message.send_action = SendAction(message_id=reply_message_id.message_id,
                                                         user_id=reply_message_id.user_id)

            if message.image.startswith('http'):
                message.image = await get_image(message.image, message.file_id)
            await UMRDriver.api_call(action.to_platform, 'send', action.to_chat, action.chat_type, message)

            self.logger.debug(f'added new task to ({action.to_platform}, {action.to_chat}, {action.chat_type})')

    def reload(self):
        pass


dispatcher: UMRDispatcher


async def dispatch(message: UnifiedMessage):
    if not dispatcher:
        pass

    await dispatcher.dispatch(message)


def init_dispatcher():
    global dispatcher
    dispatcher = UMRDispatcher()
