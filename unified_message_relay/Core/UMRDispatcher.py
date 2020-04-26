from typing import Union, List, DefaultDict, Tuple, Any, Union, Dict
import asyncio
from collections import defaultdict
from .UMRType import UnifiedMessage, ForwardAction, ForwardActionType, DefaultForwardAction,\
    DefaultForwardActionType, SendAction, ChatType, GroupID,\
    DestinationMessageID, ForwardTypeEnum, DefaultForwardTypeEnum
from . import UMRLogging
from . import UMRDriver
from .UMRConfig import config
from .UMRMessageRelation import get_message_id
from .UMRMessageHook import dispatch_hook
from .UMRFile import get_image

"""


   +-----------+    +-----------+     +-----------+    +-----------+
   |           |Yes |Normal     |     | Default   |    |           |
   |  Reply?   +--->+OneWay+    +---->+ OneWay+   +--->+ Discard   |
   |           |    |Bidirection|     |           |    |           |
   +-----------+    +-----------+     +-----------+    +-----------+
         |
       No|
         v
   +-----------+    +-----------+     +-----------+
   |           |    |           |     |           |
   |  Normal   +--->+  Default  +---->+  Discard  |
   |           |    |           |     |           |
   +-----------+    +-----------+     +-----------+



"""
class UMRDispatcher:
    def __init__(self):
        self.logger = UMRLogging.get_logger('Dispatcher')

        # bot accounts for each platform
        self.bot_accounts = config.ForwardList.Accounts

        # forward graph

        self.action_graph: DefaultDict[GroupID, List[ForwardAction]] = defaultdict(lambda: list())  # action graph

        self.default_action_graph: DefaultDict[str, Dict[GroupID, DefaultForwardAction]] = defaultdict(
            lambda: dict())  # default action graph

        # initialize action_graph
        for i in config.ForwardList.Topology:

            # Add action
            # BiDirection = two ALL
            # OneWay      = one All
            # OneWay+     = one All + one Reply

            # ForwardType.All: From one platform to another, forward all message
            # ForwardType.Reply: From one platform to another, forward only replied message

            # init forward graph and workers
            if i.ForwardType == ForwardTypeEnum.BiDirection:
                forward_action_type = ForwardActionType.ForwardAll
                backward_action_type = ForwardActionType.ForwardAll
            elif i.ForwardType == ForwardTypeEnum.OneWayPlus:
                forward_action_type = ForwardActionType.ForwardAll
                backward_action_type = ForwardActionType.ReplyOnly
            elif i.ForwardType == ForwardTypeEnum.OneWay:
                forward_action_type = ForwardActionType.ForwardAll
                backward_action_type = ForwardActionType.Block
            else:
                self.logger.warning(f'Unrecognized ForwardType in config: "{i.ForwardType}", ignoring')
                continue
            self.action_graph[GroupID(platform=i.From,
                                      chat_id=i.FromChat,
                                      chat_type=i.FromChatType)].append(
                ForwardAction(to_platform=i.To,
                              to_chat=i.ToChat,
                              chat_type=i.ToChatType,
                              action_type=forward_action_type))
            self.action_graph[
                GroupID(platform=i.To,
                        chat_id=i.ToChat,
                        chat_type=i.ToChatType)].append(
                ForwardAction(to_platform=i.From,
                              to_chat=i.FromChat,
                              chat_type=i.FromChatType,
                              action_type=backward_action_type))

        # initialize default_action_graph
        for i in config.ForwardList.Default:

            # Add action
            # OneWay      = one All
            # OneWay+     = one All + one Reply

            # ForwardType.All: From one platform to another, forward all message, accept reply backward
            # ForwardType.Reply: From one platform to another, forward all message, reject reply backward

            if i.ForwardType == DefaultForwardTypeEnum.OneWayPlus:
                action_type = DefaultForwardActionType.OneWayWithReply
            elif i.ForwardType == DefaultForwardTypeEnum.OneWay:
                action_type = DefaultForwardActionType.OneWay
            else:
                self.logger.warning(f'Unrecognized ForwardType in config: "{i.ForwardType}", ignoring')
                continue
            self.default_action_graph[i.From][
                GroupID(platform=i.To,
                        chat_id=i.ToChat,
                        chat_type=i.ToChatType)] = \
                DefaultForwardAction(to_platform=i.To,
                                     to_chat=i.ToChat,
                                     chat_type=i.ToChatType,
                                     action_type=action_type)

    async def send(self, message: UnifiedMessage, platform: str, chat_id: Union[int, str], chat_type: ChatType):
        """
        Internal function: dispatch message to destination driver

        :param message: UnifiedMessage
        :param platform: dst platform
        :param chat_id: dst chat id
        :param chat_type: dst type
        """
        if await dispatch_hook(message,
                               dst_driver=platform,
                               dst_chat=chat_id,
                               dst_chat_type=chat_type):
            self.logger.debug(f'Message to ({platform}, {chat_id}, {chat_type}) is handled by hook')
            return
        if message.image.startswith('http'):
            message.image = await get_image(message.image, message.file_id)
        await UMRDriver.api_call(platform, 'send', chat_id, chat_type, message)
        self.logger.debug(f'Message to ({platform}, {chat_id}, {chat_type}) is assigned to driver')

    async def dispatch_normal_reply(self, message: UnifiedMessage, reply_message_id: DestinationMessageID):
        # normal one way forward, ignore
        normal_action = self.action_graph[GroupID(platform=message.chat_attrs.platform,
                                                  chat_id=message.chat_attrs.chat_id,
                                                  chat_type=message.chat_attrs.chat_type)]
        for action in normal_action:  # ignore if defined, else treat as OneWay+
            if action.to_platform == reply_message_id.source.platform and action.to_chat == reply_message_id.source.chat_id:
                if action.action_type == ForwardActionType.Block:
                    return True
                break
        else:
            return False

        # if it has any action, then forward

        message.chat_attrs.reply_to = None
        message.send_action = SendAction(message_id=reply_message_id.source.message_id,
                                         user_id=reply_message_id.source.user_id)
        await self.send(message,
                        reply_message_id.source.platform,
                        reply_message_id.source.chat_id,
                        reply_message_id.source.chat_type)

        return True

    async def dispatch_default_reply(self, message: UnifiedMessage, reply_message_id: DestinationMessageID):
        # default one way forward, block
        default_action = self.default_action_graph[reply_message_id.source.platform].get(
            GroupID(platform=message.chat_attrs.platform, chat_id=message.chat_attrs.chat_id,
                    chat_type=message.chat_attrs.chat_type))
        if not default_action:
            return False

        if default_action.action_type == DefaultForwardActionType.OneWay:  # block forwarding
            return True

        # OneWayWithReply

        message.chat_attrs.reply_to = None
        message.send_action = SendAction(message_id=reply_message_id.source.message_id,
                                         user_id=reply_message_id.source.user_id)
        await self.send(message,
                        reply_message_id.source.platform,
                        reply_message_id.source.chat_id,
                        reply_message_id.source.chat_type)

        return True

    async def dispatch_reply(self, message: UnifiedMessage):
        """
        dispatch messages that replied messages forwarded by default rule
        :param message:
        :return:
        """

        # check reply
        if not message.chat_attrs.reply_to:
            return False

        # if the message is replying to a normal user, let it pass to normal dispatch
        if message.chat_attrs.reply_to.user_id != self.bot_accounts.get(message.chat_attrs.platform):
            return False

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

        if await self.dispatch_normal_reply(message, reply_message_id):
            return True

        if await self.dispatch_default_reply(message, reply_message_id):
            return True

        return False

    async def dispatch_default(self, message: UnifiedMessage):
        if not self.default_action_graph[message.chat_attrs.platform]:
            return False

        for _, action in self.default_action_graph[message.chat_attrs.platform].items():
            await self.send(message, action.to_platform, action.to_chat, action.chat_type)

        return True

    async def dispatch_normal(self, message: UnifiedMessage):
        actions = self.action_graph[GroupID(platform=message.chat_attrs.platform,
                                            chat_id=message.chat_attrs.chat_id,
                                            chat_type=message.chat_attrs.chat_type)]
        if not actions:
            return False

        for action in actions:
            if action.action_type != ForwardActionType.ForwardAll:  # reply is handled in another logic
                continue

            await self.send(message, action.to_platform, action.to_chat, action.chat_type)

        return True

    async def dispatch(self, message: UnifiedMessage):
        if await dispatch_hook(message):
            return

        # check reply
        if await self.dispatch_reply(message):
            return

        # check normal
        if await self.dispatch_normal(message):
            return

        # check default
        if await self.dispatch_default(message):
            return

    def reload(self):
        pass


dispatcher: UMRDispatcher


async def dispatch(message: UnifiedMessage):
    """
    Shadow function for dispatch's real dispatch signature
    :param message:
    :return:
    """
    if not dispatcher:
        pass

    await dispatcher.dispatch(message)


def init_dispatcher():
    global dispatcher
    dispatcher = UMRDispatcher()
