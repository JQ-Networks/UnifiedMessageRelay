from .linebotx import LineBotApiAsync, WebhookHandlerAsync, AioHttpClient
from quart import Quart, request, abort, Response, send_from_directory
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, StickerMessage, \
    StickerSendMessage, VideoMessage, AudioMessage
import asyncio
from typing import Dict, DefaultDict
from io import BytesIO
from PIL import Image
from Core import UMRLogging
from Core import UMRDriver
from Core import UMRConfig
from Core.UMRType import UnifiedMessage, MessageEntity
from Core.UMRMessageRelation import set_ingress_message_id, set_egress_message_id
from Util.Helper import check_attribute, assemble_message
import threading
import os
from uuid import uuid4
from collections import defaultdict
from ssl import SSLError
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class LineDriver(UMRDriver.BaseDriver):
    def __init__(self, name):
        self.name = name
        self.logger = UMRLogging.getLogger(f'UMRDriver.{self.name}')
        self.logger.debug(f'Started initialization for {self.name}')
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.loop.set_exception_handler(self.handle_exception)
        self.config: Dict = UMRConfig.config['Driver'][self.name]
        self.handler: WebhookHandlerAsync
        attributes = [
            'ChannelID',
            'BotToken',
            'WebHookToken',
            'WebHookURL',
            'WebHookPort',
            'HTTPSCert',
            'HTTPSKey',
            'HTTPSCA',
            'ChatList'  # chatlist is group_id: type (user, room or group)
        ]
        check_attribute(self.config, attributes, self.logger)

        self.chat_list = dict()
        self.reverse_chat_list = dict()
        self.user_names: Dict[str, str] = dict()  # [user_id, username]
        self._message_id = 0
        self._chat_id = 0
        self.data_root = UMRConfig.config['DataRoot']
        self.channel_id = self.config['ChannelID']
        self.image_webhook_url = self.config.get('WebHookURL') + ':' + str(self.config.get('WebHookPort')) + '/image/'

        for raw_chat_id, chat_type in self.config['ChatList'].items():
            self.raw_to_chat_id(raw_chat_id, chat_type)

        self.loop = asyncio.new_event_loop()

        transport = AioHttpClient(loop=self.loop)
        self.bot = LineBotApiAsync(self.config['BotToken'], http_client=transport)
        self.app = Quart(__name__)
        self.handler = WebhookHandlerAsync(self.config['WebHookToken'])

        @self.app.route("/callback", methods=['POST'])
        async def callback():
            # get X-Line-Signature header value
            signature = request.headers['X-Line-Signature']

            data = await request.get_data()

            body = data.decode()
            print("Request body: " + body)

            # handle webhook body
            try:
                await self.handler.handle(body, signature)
            except InvalidSignatureError:
                abort(400)

            return Response('OK')

        @self.app.route('/image/<path:path>')
        async def image_hosting(path):
            return await send_from_directory(self.data_root, path)

        @self.handler.add(MessageEvent)
        async def message_text(event: MessageEvent):
            if event.source.type == 'user':
                raw_chat_id = event.source.user_id
                username = await self.get_user_name(user_id=event.source.user_id)
            elif event.source.type == 'group':
                raw_chat_id = event.source.group_id
                username = await self.get_user_name(user_id=event.source.user_id, group_id=event.source.group_id)
            elif event.source.type == 'room':
                raw_chat_id = event.source.room_id
                username = await self.get_user_name(user_id=event.source.user_id, room_id=event.source.room_id)
            else:  # unknown source
                return

            chat_id = self.raw_to_chat_id(raw_chat_id, event.source.type)
            pseudo_message_id = self.message_id
            message = UnifiedMessage(platform=self.name, chat_id=chat_id, name=username, message_id=pseudo_message_id)
            set_ingress_message_id(src_platform=self.name, src_chat_id=chat_id,
                                   src_message_id=pseudo_message_id, user_id=0)
            if isinstance(event.message, TextMessage):
                message.message.append(MessageEntity(text=event.message.text))
            elif isinstance(event.message, StickerMessage):
                message.message.append(MessageEntity(text='Sent a sticker'))
            elif isinstance(event.message, ImageMessage):
                message_content = await self.bot.get_message_content(event.message.id)
                image_content = message_content.content
                image: Image.Image = Image.open(BytesIO(image_content))
                image_path = os.path.join(self.data_root, str(uuid4()) + '.jpg')
                image.save(image_path)
                message.image = image_path
            else:
                message.message.append(MessageEntity(text='Unsupported message type'))
            await UMRDriver.receive(message)

    @property
    def message_id(self):
        self._message_id += 1
        return self._message_id

    @property
    def chat_id(self):
        self._chat_id += 1
        return self._chat_id

    async def get_user_name(self, user_id, group_id=None, room_id=None):
        """
        get user name by get_profile
        :param user_id: raw user id
        :param group_id: if not None, call get_group_member_profile
        :param room_id: if not None, call get_room_member_profile
        :return: str
        """
        if user_id in self.user_names:
            return self.user_names[user_id]

        if group_id is not None:
            profile = await self.bot.get_group_member_profile(group_id=group_id, user_id=user_id)
        elif room_id is not None:
            profile = await self.bot.get_room_member_profile(room_id=room_id, user_id=user_id)
        else:
            profile = await self.bot.get_profile(user_id=user_id)

        self.user_names[user_id] = profile.display_name
        return profile.display_name

    def chat_id_to_raw(self, chat_id):
        return self.chat_list.get(chat_id)

    def raw_to_chat_id(self, raw_chat_id, chat_type='user'):
        chat_id = self.reverse_chat_list.get(raw_chat_id)
        if not chat_id:
            if chat_type == 'user':
                chat_id = self.chat_id
            elif chat_type in ('room', 'group'):
                chat_id = -self.chat_id
            self.reverse_chat_list[raw_chat_id] = chat_id
            self.chat_list[chat_id] = raw_chat_id
        return chat_id

    def start(self):
        async def shutdown():
            await self.bot.close()

        def run():
            nonlocal self
            asyncio.set_event_loop(self.loop)
            self.app.run(host='0.0.0.0', port=self.config['WebHookPort'], loop=self.loop, shutdown_trigger=shutdown,
                         ca_certs=self.config['HTTPSCA'],
                         keyfile=self.config['HTTPSKey'],
                         certfile=self.config['HTTPSCert'])

        t = threading.Thread(target=run)
        t.daemon = True
        UMRDriver.threads.append(t)
        t.start()

        self.logger.debug(f'Finished initialization for {self.name}')

    async def send(self, to_chat: int, messsage: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('calling real send')
        return asyncio.run_coroutine_threadsafe(self._send(to_chat, messsage), self.loop)

    async def _send(self, to_chat: int, message: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('begin processing message')

        raw_chat_id = self.chat_id_to_raw(to_chat)

        message_prefix = ''
        if message.chat_attrs.name:
            message_prefix = message.chat_attrs.name
        if message.chat_attrs.reply_to:
            message_prefix += ' (➡️️' + message.chat_attrs.reply_to.name + ')'
        if message.chat_attrs.forward_from:
            message_prefix += ' (️️↩️' + message.chat_attrs.forward_from.name + ')'
        if message.chat_attrs.name:
            message_prefix += ': '

        if message.message:
            message_text = assemble_message(message)
            await self.bot.push_message(to=raw_chat_id, messages=TextSendMessage(text=message_prefix + message_text))
        if message.image:
            _, original_file_name = os.path.split(message.image)
            file_name, file_ext = original_file_name.split('.')
            image_original = file_name + '-origin.' + file_ext
            image_thumb = file_name + '-thumb.' + file_ext
            image_original_path = os.path.join(self.data_root, image_original)
            image_thumb_path = os.path.join(self.data_root, image_thumb)

            if not os.path.isfile(image_original_path):
                image: Image.Image = Image.open(message.image)
                image.thumbnail((1024, 1024), Image.ANTIALIAS)
                image.save(image_original_path)
                image.thumbnail((240, 240), Image.ANTIALIAS)
                image.save(image_thumb_path)

            await self.bot.push_message(to=raw_chat_id, messages=TextSendMessage(text=message_prefix + 'Sent an image ⬇️'))
            self.logger.debug('Begin sending image')
            await self.bot.push_message(to=raw_chat_id,
                                        messages=ImageSendMessage(original_content_url=self.image_webhook_url + image_original,
                                                                  preview_image_url=self.image_webhook_url + image_thumb)
            )
            self.logger.debug('Finished sending image')
        if message.chat_attrs:
            set_egress_message_id(src_platform=message.chat_attrs.platform,
                                  src_chat_id=message.chat_attrs.chat_id,
                                  src_message_id=message.chat_attrs.message_id,
                                  dst_platform=self.name,
                                  dst_chat_id=to_chat,
                                  dst_message_id=self.message_id,  # useless message id
                                  user_id=0)

    def handle_exception(self, loop, context):
        # e = context.get('exception')
        # if isinstance(e, SSLError):
        #     return
        msg = context.get("exception", context["message"])
        self.logger.exception('Unhandled exception: ', exc_info=msg)

    async def is_group_admin(self, chat_id: int, user_id: int):
        return False

    async def is_group_owner(self, chat_id: int, user_id: int):
        return False


UMRDriver.register_driver('Line', LineDriver)
