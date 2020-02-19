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
from Util.Helper import check_attribute, unparse_entities_to_html


class TelegramDriver(UMRDriver.BaseDriver):
    def __init__(self, name):
        self.name = name

        # Initialize bot and dispatcher
        self.logger = UMRLogging.getLogger(f'UMRDriver.{self.name}')
        self.logger.debug(f'Started initialization for {self.name}')

        attributes = [
            ('BotToken', False, None)
        ]
        self.config = UMRConfig.config['Driver'][self.name]
        check_attribute(self.config, attributes, self.logger)
        self.bot: Bot
        self.bot_user_id = int(self.config['BotToken'].split(':')[0])
        self.image_file_id: Dict[str, str] = dict()  # mapping from filename to existing file id
        self.loop: asyncio.AbstractEventLoop


    def start(self):
        def run():
            nonlocal self
            self.logger.debug('Running start')
            self.loop = asyncio.new_event_loop()
            self.loop.set_exception_handler(self.handle_exception)
            asyncio.set_event_loop(self.loop)
            self.bot = Bot(token=self.config['BotToken'])
            self.dp = Dispatcher(self.bot)

            @self.dp.message_handler(content_types=ContentType.ANY)
            @self.dp.edited_message_handler(content_types=ContentType.ANY)
            async def handle_msg(message: types.Message):
                from_user = message.from_user
                _chat_type = ChatType.GROUP if message.chat.id < 0 else ChatType.PRIVATE

                if message.text:
                    text = message.text
                elif message.caption:
                    text = message.caption
                else:
                    text = ''

                message_entities = self.parse_entities(message)

                unified_message = UnifiedMessage(platform=self.name,
                                                 message=text,
                                                 message_entities=message_entities,
                                                 chat_id=message.chat.id,
                                                 chat_type=_chat_type,
                                                 name=from_user.full_name,
                                                 user_id=from_user.id,
                                                 message_id=message.message_id)

                self.get_chat_attributes(message, unified_message.chat_attrs)
                set_ingress_message_id(src_platform=self.name, src_chat_id=message.chat.id, src_chat_type=_chat_type,
                                       src_message_id=message.message_id, user_id=message.from_user.id)

                if message.content_type == ContentType.TEXT:
                    await UMRDriver.receive(unified_message)
                elif message.content_type == ContentType.PHOTO:
                    url, file_id = await self.tg_get_image(message.photo[-1].file_id)
                    unified_message.image = url
                    unified_message.file_id = file_id
                    await UMRDriver.receive(unified_message)
                elif message.content_type == ContentType.STICKER:
                    url, file_id = await self.tg_get_image(message.sticker.file_id)
                    unified_message.image = url
                    unified_message.file_id = file_id
                    await UMRDriver.receive(unified_message)
                elif message.content_type == ContentType.ANIMATION:
                    url, file_id = await self.tg_get_image(message.animation.file_id)
                    unified_message.image = url
                    unified_message.file_id = file_id
                    await UMRDriver.receive(unified_message)
                else:
                    unified_message.message = '[Unsupported message]'
                    await UMRDriver.receive(unified_message)
            executor.start_polling(self.dp, skip_updates=True, loop=self.loop)

        t = threading.Thread(target=run)
        t.daemon = True
        UMRDriver.threads.append(t)
        t.start()

        self.logger.debug(f'Finished initialization')

    async def send(self, to_chat: Union[int, str], chat_type: ChatType, message: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('calling real send')
        return asyncio.run_coroutine_threadsafe(self._send(to_chat, message), self.loop)

    async def _send(self, to_chat: int, message: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('begin processing message')
        await self.bot.send_chat_action(to_chat, types.chat.ChatActions.TYPING)
        if message.chat_attrs.name:
            text = '<b>' + message.chat_attrs.name + '</b>: '
        else:
            text = ''

        text += unparse_entities_to_html(message,
                                         EntityType.LINK | EntityType.STRIKETHROUGH | EntityType.UNDERLINE |
                                         EntityType.CODE_BLOCK | EntityType.BOLD | EntityType.ITALIC |
                                         EntityType.PLAIN | EntityType.CODE)

        if message.send_action.message_id:
            reply_to_message_id = message.send_action.message_id
        else:
            reply_to_message_id = None  # TODO support cross platform reply in the future

        if message.image:
            if message.image in self.image_file_id:
                self.logger.debug(f'file id for {message.image} found, sending file id')
                if message.image.endswith('gif'):
                    tg_message = await self.bot.send_animation(to_chat, self.image_file_id[message.image], caption=text,
                                                               parse_mode=types.message.ParseMode.HTML,
                                                               reply_to_message_id=reply_to_message_id)
                else:
                    tg_message = await self.bot.send_photo(to_chat, self.image_file_id[message.image], caption=text,
                                                           parse_mode=types.message.ParseMode.HTML,
                                                           reply_to_message_id=reply_to_message_id)
            else:
                self.logger.debug(f'file id for {message.image} not found, sending image file')
                if message.image.endswith('gif'):
                    tg_message = await self.bot.send_animation(to_chat, types.input_file.InputFile(message.image),
                                                               caption=text,
                                                               parse_mode=types.message.ParseMode.HTML,
                                                               reply_to_message_id=reply_to_message_id)
                    self.image_file_id[message.image] = tg_message.document.file_id
                else:
                    tg_message = await self.bot.send_photo(to_chat, types.input_file.InputFile(message.image),
                                                           caption=text,
                                                           parse_mode=types.message.ParseMode.HTML,
                                                           reply_to_message_id=reply_to_message_id)
                    self.image_file_id[message.image] = tg_message.photo[-1].file_id
        else:
            self.logger.debug('finished processing message, ready to send')
            tg_message = await self.bot.send_message(to_chat, text, parse_mode=types.message.ParseMode.HTML,
                                                     reply_to_message_id=reply_to_message_id)

        if message.chat_attrs:
            set_egress_message_id(src_platform=message.chat_attrs.platform,
                                  src_chat_id=message.chat_attrs.chat_id,
                                  src_chat_type=message.chat_attrs.chat_type,
                                  src_message_id=message.chat_attrs.message_id,
                                  dst_platform=self.name,
                                  dst_chat_id=to_chat,
                                  dst_chat_type=ChatType.GROUP if to_chat < 0 else ChatType.PRIVATE,
                                  dst_message_id=tg_message.message_id,
                                  user_id=self.bot_user_id)
        self.logger.debug('finished sending')
        return tg_message.message_id

    def parse_entities(self, message: types.Message):
        if message.entities:
            entities = message.entities
        elif message.caption_entities:
            entities = message.caption_entities
        else:
            return None

        result = list()

        for entity in entities:
            entity_map = {
                'mention':       EntityType.BOLD,
                'hashtag':       EntityType.PLAIN,
                'cashtag':       EntityType.PLAIN,
                'bot_command':   EntityType.PLAIN,
                'url':           EntityType.PLAIN,
                'email':         EntityType.PLAIN,
                'phone_number':  EntityType.PLAIN,
                'bold':          EntityType.BOLD,
                'italic':        EntityType.ITALIC,
                'underline':     EntityType.UNDERLINE,
                'strikethrough': EntityType.STRIKETHROUGH,
                'code':          EntityType.CODE,
                'pre':           EntityType.CODE_BLOCK,
                'text_mention':  EntityType.BOLD,
                'text_link':     EntityType.LINK
            }
            if entity.type == 'text_link':
                url = entity.url
            else:
                url = ''

            result.append(MessageEntity(start=entity.offset, end=entity.offset+entity.length,
                                        entity_type=entity_map[entity.type], link=url))
        return result

    async def tg_get_image(self, file_id) -> (str, str):
        """

        :param file_id:
        :return:
        """
        file = await self.bot.get_file(file_id)
        url = f'https://api.telegram.org/file/bot{self.config["BotToken"]}/{file.file_path}'
        perm_id = file_id[-52:]
        return url, perm_id

    def get_chat_attributes(self, message: types.Message, chat_attrs: ChatAttribute):
        if message.forward_from_chat:  # forward from channel or user's private chat
            if message.forward_from_chat.title:
                name = message.forward_from_chat.title
                chat_id = message.forward_from_chat.id
                user_id = 0
                message_id = message.forward_from_message_id
            else:
                name = message.forward_from_chat.full_name
                chat_id = message.forward_from_chat.id
                user_id = message.forward_from_chat.id
                message_id = 0
            # private message does not have message_id, and channel message does not have user_id
            chat_attrs.forward_from = ChatAttribute(platform=self.name,
                                                    chat_id=chat_id,
                                                    chat_type=ChatType.GROUP if message.chat.id < 0 else ChatType.PRIVATE,
                                                    user_id=user_id,
                                                    name=name,
                                                    message_id=message_id)

        if message.forward_sender_name:
            chat_attrs.forward_from = ChatAttribute(platform=self.name,
                                                    name=message.forward_sender_name)

        if message.forward_from:  # forward from user (group message)
            name = message.forward_from.full_name
            user_id = message.forward_from.id
            # forward message does not have message_id and chat_id
            chat_attrs.forward_from = ChatAttribute(platform=self.name,
                                                    chat_type=ChatType.PRIVATE,
                                                    chat_id=0,
                                                    user_id=user_id,
                                                    name=name)

        if message.reply_to_message:
            chat_attrs.reply_to = ChatAttribute(platform=self.name,
                                                chat_id=message.reply_to_message.chat.id,
                                                chat_type=ChatType.GROUP if message.reply_to_message.chat.id < 0 else ChatType.PRIVATE,
                                                name=message.reply_to_message.from_user.full_name,
                                                user_id=message.reply_to_message.from_user.id,
                                                message_id=message.reply_to_message.message_id)
            self.get_chat_attributes(message.reply_to_message, chat_attrs.reply_to)

    async def is_group_admin(self, chat_id: int, chat_type: ChatType, user_id: int):
        if chat_type != ChatType.GROUP:
            return False
        member = await self.bot.get_chat_member(chat_id, user_id)
        if member:
            if member.status in ('creator', 'administrator'):
                return True
        return False

    async def is_group_owner(self, chat_id: int, chat_type: ChatType, user_id: int):
        if chat_type != ChatType.GROUP:
            return False
        member = await self.bot.get_chat_member(chat_id, user_id)
        if member:
            if member.status == 'creator':
                return True
        return False

    def handle_exception(self, loop, context):
        # context["message"] will always be there; but context["exception"] may not
        msg = context.get("exception", context["message"])
        self.logger.exception('Unhandled exception: ', exc_info=msg)


UMRDriver.register_driver('Telegram', TelegramDriver)
