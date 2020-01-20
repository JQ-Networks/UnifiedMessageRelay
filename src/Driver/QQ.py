import threading
import asyncio
import janus
from aiocqhttp import CQHttp, ApiError, MessageSegment
from Core.UnifiedMessage import UnifiedMessage
from Core import CTBDriver

NAME = 'QQ'

bot = CQHttp(api_root='http://127.0.0.1:5700/',
             access_token='very',
             secret='long')


@bot.on_message
# 上面这句等价于 @bot.on('message')
async def handle_msg(context):
    # 下面这句等价于 bot.send_private_msg(user_id=context['user_id'], message='你好呀，下面一条是你刚刚发的：')
    try:
        message = UnifiedMessage('QQ', context.get('group_id'), context.get('user_id'), '', context.get('raw_message'),
                                 '')
        await CTBDriver.receive(message)
    except ApiError:
        pass
    return {}  # 返回给 HTTP API 插件，走快速回复途径


async def send(to_chat: int, messsage: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    context = dict()
    context['message_type'] = 'group'
    context['message'] = MessageSegment.text(messsage.message)
    context['group_id'] = to_chat
    await bot.send(context, context['message'])


CTBDriver.sender['QQ'] = send


async def async_coro(async_q):
    while True:
        to_chat, message = await async_q.get()
        await send(to_chat, message)
        async_q.task_done()


def run():
    loop = asyncio.get_event_loop()
    queue = janus.Queue(loop=loop)
    CTBDriver.janus_queue['QQ'] = queue
    loop.create_task(async_coro(queue.async_q))
    bot.run(host='172.17.0.1', port=8080)


CTBDriver.set_run_blocking(run)
# t = threading.Thread(target=run)
# CTBDriver.threads.append(t)
# t.start()
