import threading
import asyncio
from typing import Dict, Union, List
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentType
from Core.UMRType import UnifiedMessage, MessageEntity, ChatAttribute, ChatType, EntityType
from Core import UMRDriver
from Core import UMRLogging
from Core import UMRConfig
from Core.UMRMessageRelation import set_ingress_message_id, set_egress_message_id
from Util.Helper import check_attribute, unparse_entities_to_markdown
import discord
import re


bold_text = re.compile(r'(?:(?<=^)|(?<=[^*]))\*\*(.*?)\*\*(?:(?=$)|(?=[^*]))', re.RegexFlag.DOTALL)
underline_text = re.compile(r'(?:(?<=^)|(?<=[^_]))__(.*?)__(?:(?=$)|(?=[^_]))', re.RegexFlag.DOTALL)
strikethrough_text = re.compile(r'(?:(?<=^)|(?<=[^~]))~~(.*?)~~(?:(?=$)|(?=[^~]))', re.RegexFlag.DOTALL)
italic_text1 = re.compile(r'(?:(?<=^)|(?<=[^*]))\*(.*?)\*(?:(?=$)|(?=[^*]))', re.RegexFlag.DOTALL)
italic_text2 = re.compile(r'(?:(?<=^)|(?<=[^_]))_(.*?)_(?:(?=$)|(?=[^_]))', re.RegexFlag.DOTALL)
code_text = re.compile(r'(?:(?<=^)|(?<=[^`]))`(.*?)`(?:(?=$)|(?=[^`]))', re.RegexFlag.DOTALL)
code_block_text = re.compile(r'(?:(?<=^)|(?<=[^`]))```(.*?)```(?:(?=$)|(?=[^`]))', re.RegexFlag.DOTALL)
quote_block_text = re.compile(r'^>>> (.*)', re.RegexFlag.DOTALL)
quote_text = re.compile(r'^> (.*)')
at_user_text = re.compile(r'<@(\d+)>')

ordered_match_list = [
    (quote_block_text, EntityType.QUOTE_BLOCK),
    (quote_text, EntityType.QUOTE),
    (code_block_text, EntityType.CODE_BLOCK),
    (code_text, EntityType.CODE),
    (bold_text, EntityType.BOLD),
    (underline_text, EntityType.UNDERLINE),
    (strikethrough_text, EntityType.STRIKETHROUGH),
    (italic_text1, EntityType.ITALIC),
    (italic_text2, EntityType.ITALIC)
]


def find_markdown(text: str, text_start: int = 0, text_end=-1, real_start: int = 0) -> (str, List[MessageEntity]):
    """
    find nearest markdown block
    :param real_start: offset in plain text
    :param text_start: start pos in markdown text
    :param text_end: end pos in markdown text
    :param text: whole markdown text
    :return: matched_text, entity_list
    """
    if text_end == -1:
        text_end = len(text)

    pos_list = list()
    entity_list: List[MessageEntity] = list()
    result = ''
    while True:
        pos_list.clear()
        text_slice = text[text_start:text_end]
        for regex_matcher, entity_type in ordered_match_list:
            try:
                _result = next(regex_matcher.finditer(text_slice))
                pos_list.append((_result, entity_type))
            except StopIteration:
                pass

        if not pos_list:
            return result + text_slice, entity_list

        match, entity_type = min(pos_list, key=lambda x: x[0].span(0)[0])
        outer_start = match.span(0)[0] + text_start
        outer_end = match.span(0)[1] + text_start
        inner_start = match.span(1)[0] + text_start
        inner_end = match.span(1)[1] + text_start
        delta = text[text_start:outer_start]
        real_start = real_start + len(delta)
        result += delta

        if entity_type not in (EntityType.CODE, EntityType.CODE_BLOCK):
            delta, _entity_list = find_markdown(text, inner_start, inner_end, real_start)
        else:
            delta = text[inner_start:inner_end]
            _entity_list = list()

        message_entity = MessageEntity(start=real_start,
                                       end=real_start + len(delta),
                                       entity_type=entity_type)
        entity_list.append(message_entity)
        real_start = real_start + len(delta)
        result += delta
        entity_list.extend(_entity_list)

        text_start = outer_end


class DiscordDriver(UMRDriver.BaseDriver, discord.Client):
    def __init__(self, name: str):
        self.loop = asyncio.new_event_loop()
        self.loop.set_exception_handler(self.handle_exception)
        discord.Client.__init__(self, loop=self.loop)

        self.name = name
        self.logger = UMRLogging.getLogger(self.name)

        self.config = UMRConfig.config['Driver'].get(self.name)
        attributes = [
            'BotToken',
            'ClientToken'
        ]
        check_attribute(self.config, attributes, self.logger)

    def start(self):
        def run():
            nonlocal self
            self.logger.debug('Running start')
            asyncio.set_event_loop(self.loop)
            self.run(self.config['BotToken'])

        t = threading.Thread(target=run)
        t.daemon = True
        UMRDriver.threads.append(t)
        t.start()

        self.logger.debug(f'Finished initialization')

    def run(self, *args, **kwargs):
        """
        monkey patched start
        """
        loop = self.loop

        async def runner():
            try:
                await discord.Client.start(self, *args, **kwargs)
            finally:
                await self.close()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.logger.info('Received signal to terminate bot and event loop.')
        finally:
            future.remove_done_callback(stop_loop_on_completion)
            self.logger.info('Cleaning up tasks.')
            discord.client._cleanup_loop(loop)

        if not future.cancelled():
            return future.result()

    async def on_ready(self):
        self.logger.info('Logged on as ' + str(self.user))

    async def on_message(self, message: discord.Message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        self.logger.debug(message)

        if isinstance(message.author, discord.User):
            from_user = message.author.display_name
            user_id = message.author.id
        elif isinstance(message.author, discord.Member):
            from_user = message.author.display_name
            user_id = message.author.id
        else:
            self.logger.debug(f'Unseen user type: {str(message.author)}')
            from_user = message.author.display_name
            user_id = message.author.id

        if isinstance(message.channel, discord.DMChannel):
            _chat_type = ChatType.PRIVATE
        elif isinstance(message.channel, discord.GroupChannel):
            _chat_type = ChatType.GROUP
        elif isinstance(message.channel, discord.TextChannel):
            _chat_type = ChatType.GROUP
        else:
            self.logger.warning('Unsupported channel type')
            return

        chat_id = message.channel.id

        unified_message = UnifiedMessage(platform=self.name,
                                         chat_id=chat_id,
                                         chat_type=_chat_type,
                                         name=from_user,
                                         user_id=user_id,
                                         message_id=message.id)

        message_content = await self.parse_at(message.content)
        unified_message.message, unified_message.message_entities = find_markdown(message_content)

        if message.attachments:
            if message.attachments[0].proxy_url:
                unified_message.image = message.attachments[0].proxy_url
            if len(message.attachments) > 1:
                self.logger.warning('More than one attachment detected, not sure how it happens')

        set_ingress_message_id(src_platform=self.name, src_chat_id=chat_id, src_chat_type=_chat_type,
                               src_message_id=message.id, user_id=user_id)

        await UMRDriver.receive(unified_message)

    async def parse_at(self, message: str):
        user_ids = at_user_text.findall(message)
        if not user_ids:
            return message
        user_name_map = dict()
        for i in user_ids:
            try:
                user_id = int(i)
                user_name_map[user_id] = self.get_user(user_id).display_name
            except:
                pass

        def sub_username(match_obj):
            try:
                user_id = int(match_obj.group(1))
                return '@' + user_name_map[user_id]
            except:
                pass
            return '@unknown'

        message = at_user_text.sub(sub_username, message)
        return message


    async def send(self, to_chat: Union[int, str], chat_type: ChatType, message: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('calling real send')
        return asyncio.run_coroutine_threadsafe(self._send(to_chat, chat_type, message), self.loop)

    async def _send(self, to_chat: int, chat_type: ChatType, message: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """

        channel = self.get_channel(to_chat)
        if not channel:
            self.logger.error(f'Chat {to_chat} not found, please check your configuration')

        message_text = ''

        # name logic
        if message.chat_attrs.name:
            message_text += message.chat_attrs.name
        if message.chat_attrs.reply_to:
            message_text += ' (➡️️' + message.chat_attrs.reply_to.name + ')'
        if message.chat_attrs.forward_from:
            message_text += ' (️️↩️' + message.chat_attrs.forward_from.name + ')'
        if message.chat_attrs.name:
            message_text += ': '

        # at user
        if message.send_action.user_id:
            message_text += f'<@{message.send_action.user_id}> '

        message_text += unparse_entities_to_markdown(message,
                                                     EntityType.PLAIN | EntityType.BOLD | EntityType.ITALIC |
                                                     EntityType.CODE | EntityType.STRIKETHROUGH | EntityType.UNDERLINE |
                                                     EntityType.CODE_BLOCK | EntityType.QUOTE | EntityType.QUOTE_BLOCK)

        if message.image:
            assert isinstance(channel, discord.TextChannel)
            outbound_message = await channel.send(content=message_text, file=discord.File(message.image))
        else:
            outbound_message = await channel.send(content=message_text)

        if message.chat_attrs:
            set_egress_message_id(src_platform=message.chat_attrs.platform,
                                  src_chat_id=message.chat_attrs.chat_id,
                                  src_chat_type=message.chat_attrs.chat_type,
                                  src_message_id=message.chat_attrs.message_id,
                                  dst_platform=self.name,
                                  dst_chat_id=to_chat,
                                  dst_chat_type=chat_type,
                                  dst_message_id=outbound_message.id,  # useless message id
                                  user_id=0)


    def handle_exception(self, loop, context):
        # context["message"] will always be there; but context["exception"] may not
        msg = context.get("exception", context["message"])
        self.logger.exception('Unhandled exception: ', exc_info=msg)


UMRDriver.register_driver('Discord', DiscordDriver)
