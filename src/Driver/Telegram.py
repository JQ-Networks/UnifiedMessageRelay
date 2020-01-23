import threading
import logging
import asyncio
import janus
from aiogram import Bot, Dispatcher, executor, types
from Core.CTBType import UnifiedMessage
from Core import CTBDriver
from Core import CTBLogging
from Core import CTBConfig
from Util.Helper import check_attribute, janus_queue_put_sync
import datetime
launch_time = datetime.datetime.now()


NAME = 'Telegram'

# Initialize bot and dispatcher

logger = CTBLogging.getLogger('CTBDriver.Telegram')

attributes = [
    'BotToken'
]
config = CTBConfig.config['Driver']['Telegram']
check_attribute(config, attributes, logger)
bot: Bot
loop: asyncio.AbstractEventLoop


async def send(to_chat: int, messsage: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    asyncio.run_coroutine_threadsafe(_send(to_chat, messsage), loop)


async def _send(to_chat: int, messsage: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    await bot.send_chat_action(to_chat, types.chat.ChatActions.TYPING)
    await bot.send_message(to_chat, messsage.forward_attrs.from_user + ':' + messsage.message)

CTBDriver.api_lookup['Telegram']['send'] = send


def run():
    global bot, dp, loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = Bot(token=config['BotToken'])
    dp = Dispatcher(bot)

    @dp.message_handler()
    async def handle_msg(message: types.Message):
        from_user = message.from_user
        reply_to = ''
        if message.reply_to_message:
            reply_to_user = message.reply_to_message.from_user
            reply_to = reply_to_user.full_name
        forward_from = ''
        if message.forward_from:
            forward_from = message.from_user.full_name
        elif message.forward_from_chat and message.forward_from_chat.type == types.chat.ChatType.CHANNEL:
            forward_from = message.forward_from_chat.title
        # message = UnifiedMessage('Telegram', message.chat.id, message.from_user.full_name, '', message.text, '')
        unified_message = UnifiedMessage(message=message.text, from_platform='Telegram', from_chat=message.chat.id,
                                         from_user=from_user.full_name, forward_from=forward_from, reply_to=reply_to)
        await CTBDriver.receive(unified_message)

    executor.start_polling(dp, skip_updates=True, loop=loop)


t = threading.Thread(target=run)
CTBDriver.threads.append(t)
t.start()
