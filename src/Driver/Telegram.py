import threading
import logging
import asyncio
import janus
from aiogram import Bot, Dispatcher, executor, types
from Core.UnifiedMessage import UnifiedMessage
from Core import CTBDriver
from Utils.Helper import test_attribute

NAME = 'Telegram'

# Initialize bot and dispatcher

logger = logging.getLogger('CTBDriver.Telegram')
attributes = [
    'TG_TOKEN'
]

test_attribute(CTBDriver.CONFIG, attributes, logger)
bot: Bot
dp: Dispatcher


async def send(to_chat: int, messsage: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    await bot.send_message(to_chat, messsage.message)


CTBDriver.sender['Telegram'] = send


async def async_coro(async_q):
    while True:
        to_chat, message = await async_q.get()
        await send(to_chat, message)
        async_q.task_done()


def run():
    global bot, dp
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    queue = janus.Queue(loop=loop)
    CTBDriver.janus_queue['Telegram'] = queue
    loop.create_task(async_coro(queue.async_q))
    bot = Bot(token=CTBDriver.CONFIG['TG_TOKEN'])
    dp = Dispatcher(bot)

    @dp.message_handler()
    async def handle_msg(message: types.Message):
        message = UnifiedMessage('Telegram', message.chat.id, message.from_user.full_name, '', message.text, '')

        await CTBDriver.receive(message)

    executor.start_polling(dp, skip_updates=True, loop=loop)


t = threading.Thread(target=run)
CTBDriver.threads.append(t)
t.start()
