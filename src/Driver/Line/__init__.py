from .linebotx import LineBotApiAsync, WebhookHandlerAsync, HttpXClient
from quart import Quart, request, abort, Response, send_from_directory
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, StickerMessage, \
    StickerSendMessage, VideoMessage, AudioMessage
import asyncio
from typing import Dict, DefaultDict, Union
from io import BytesIO
from PIL import Image
from Core import UMRLogging
from Core import UMRDriver
from Core import UMRConfig
from Core.UMRType import UnifiedMessage, MessageEntity, ChatType, EntityType
from Core.UMRMessageRelation import set_ingress_message_id, set_egress_message_id
from Util.Helper import check_attribute, unparse_entities_to_markdown
import threading
import os
from uuid import uuid4
from collections import defaultdict
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


class LineDriver(UMRDriver.BaseDriverMixin):
    def __init__(self, name):
        self.name = name
        self.logger = UMRLogging.get_logger(f'UMRDriver.{self.name}')
        self.logger.debug(f'Started initialization for {self.name}')
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.loop.set_exception_handler(self.handle_exception)
        self.config: Dict = UMRConfig.config['Driver'][self.name]
        self.handler: WebhookHandlerAsync
        attributes = [
            ('ChannelID', False, None),
            ('BotToken', False, None),
            ('WebHookToken', False, None),
            ('WebHookURL', False, None),
            ('WebHookPort', False, None),
            ('HTTPSCert', False, None),
            ('HTTPSKey', False, None),
            ('HTTPSCA', False, None),
        ]
        check_attribute(self.config, attributes, self.logger)

        self.user_names: Dict[str, str] = dict()  # [user_id, username]
        self._message_id = 0
        self.data_root = UMRConfig.config['DataRoot']
        self.channel_id = self.config['ChannelID']
        self.image_webhook_url = self.config.get('WebHookURL') + ':' + str(self.config.get('WebHookPort')) + '/image/'

        # mapping between internal type and external type
        self.chat_type_dict = {
            'user': ChatType.PRIVATE,
            'room': ChatType.DISCUSS,
            'group': ChatType.GROUP
        }

        self.chat_type_dict_reversed = {v: k for k, v in self.chat_type_dict.items()}

        self.loop = asyncio.new_event_loop()

        transport = HttpXClient()
        self.bot = LineBotApiAsync(self.config['BotToken'], http_client=transport)
        self.app = Quart(__name__)
        self.handler = WebhookHandlerAsync(self.config['WebHookToken'])

        # previous reply token, try to save push api limit
        self.reply_token: DefaultDict[str, str] = defaultdict(lambda: '')

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
                chat_id = event.source.user_id
                username = await self.get_user_name(user_id=event.source.user_id)
            elif event.source.type == 'group':
                chat_id = event.source.group_id
                username = await self.get_user_name(user_id=event.source.user_id, group_id=event.source.group_id)
            elif event.source.type == 'room':
                chat_id = event.source.room_id
                username = await self.get_user_name(user_id=event.source.user_id, room_id=event.source.room_id)
            else:  # unknown source
                return

            _chat_type = self.chat_type_dict[event.source.type]
            pseudo_message_id = self.message_id
            message = UnifiedMessage(platform=self.name, chat_id=chat_id, chat_type=_chat_type, name=username, message_id=pseudo_message_id)
            set_ingress_message_id(src_platform=self.name, src_chat_id=chat_id, src_chat_type=_chat_type,
                                   src_message_id=pseudo_message_id, user_id=0)
            if isinstance(event.message, TextMessage):
                message.message = event.message.text
            elif isinstance(event.message, StickerMessage):
                message.message = 'Sent a sticker'
            elif isinstance(event.message, ImageMessage):
                message_content = await self.bot.get_message_content(event.message.id)
                image_content = message_content.content
                image: Image.Image = Image.open(BytesIO(image_content))
                image_path = os.path.join(self.data_root, str(uuid4()) + '.jpg')
                image.save(image_path)
                message.image = image_path
            else:
                message.message = 'Unsupported message type'
            await self.receive(message)

    @property
    def message_id(self):
        self._message_id += 1
        return self._message_id

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

    def start(self):

        def run():
            nonlocal self
            asyncio.set_event_loop(self.loop)

            task = self.app.run_task(host='0.0.0.0', port=self.config['WebHookPort'],
                                     ca_certs=self.config['HTTPSCA'],
                                     keyfile=self.config['HTTPSKey'],
                                     certfile=self.config['HTTPSCert'])

            self.loop.create_task(task)
            self.loop.run_forever()

        t = threading.Thread(target=run)
        t.daemon = True
        UMRDriver.threads.append(t)
        t.start()

        self.logger.debug(f'Finished initialization for {self.name}')

    async def send(self, to_chat: Union[int, str], chat_type: ChatType, messsage: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('calling real send')
        return asyncio.run_coroutine_threadsafe(self._send(to_chat, chat_type, messsage), self.loop)

    async def _send(self, to_chat: str, chat_type: ChatType, message: UnifiedMessage):
        """
        decorator for send new message
        :return:
        """
        self.logger.debug('begin processing message')

        _chat_type = self.chat_type_dict_reversed[chat_type]

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
            message_text = unparse_entities_to_markdown(message, EntityType.PLAIN)
            _message = TextSendMessage(text=message_prefix + message_text)
            await self.bot.push_message(to=to_chat, messages=_message)
        if message.image:
            _, original_file_name = os.path.split(message.image)
            file_name, file_ext = original_file_name.split('.')
            image_original = file_name + '-origin.' + file_ext
            image_thumb = file_name + '-thumb.' + file_ext
            image_original_path = os.path.join(self.data_root, image_original)
            image_thumb_path = os.path.join(self.data_root, image_thumb)

            if not os.path.isfile(image_original_path):
                image: Image.Image = Image.open(message.image)
                if image.size[0] <= 1024 and image.size[1] <= 1024:
                    image_original = original_file_name
                else:
                    image.thumbnail((1024, 1024), Image.ANTIALIAS)
                    image.save(image_original_path)
                image.thumbnail((240, 240), Image.ANTIALIAS)
                image.save(image_thumb_path)

            await self.bot.push_message(to=to_chat, messages=TextSendMessage(text=message_prefix + 'Sent an image ⬇️'))
            self.logger.debug('Begin sending image')
            await self.bot.push_message(to=to_chat,
                                        messages=ImageSendMessage(original_content_url=self.image_webhook_url + image_original,
                                                                  preview_image_url=self.image_webhook_url + image_thumb)
            )
            self.logger.debug('Finished sending image')
        if message.chat_attrs:
            set_egress_message_id(src_platform=message.chat_attrs.platform,
                                  src_chat_id=message.chat_attrs.chat_id,
                                  src_chat_type=message.chat_attrs.chat_type,
                                  src_message_id=message.chat_attrs.message_id,
                                  dst_platform=self.name,
                                  dst_chat_id=to_chat,
                                  dst_chat_type=_chat_type,
                                  dst_message_id=self.message_id,  # useless message id
                                  user_id=0)

    def handle_exception(self, loop, context):
        # e = context.get('exception')
        # if isinstance(e, SSLError):
        #     return
        msg = context.get("exception", context["message"])
        self.logger.exception('Unhandled exception: ', exc_info=msg)

    async def is_group_admin(self, chat_id: int, chat_type: ChatType, user_id: int):
        return False

    async def is_group_owner(self, chat_id: int, chat_type: ChatType, user_id: int):
        return False


UMRDriver.register_driver('Line', LineDriver)
