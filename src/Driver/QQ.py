from typing import Dict
import threading
import asyncio
import janus
from cqhttp import CQHttp
from aiocqhttp import MessageSegment
from Core.CTBType import UnifiedMessage
from Core import CTBDriver
from Core import CTBLogging
from Util.Helper import janus_queue_put_sync, check_attribute
from Core import CTBConfig

NAME = 'QQ'

logger = CTBLogging.getLogger('CTBDriver.QQ')

loop: asyncio.AbstractEventLoop
queue: janus.Queue

config: Dict = CTBConfig.config['Driver']['QQ']

attributes = [
    'APIRoot',
    'ListenIP',
    'ListenPort',
    'Token',
    'Secret',
]
check_attribute(config, attributes, logger)
bot = CQHttp(api_root=config.get('APIRoot'),
             access_token=config.get('Token'),
             secret=config.get('Secret'))


##### Define send and receive #####

@bot.on_message()
# 上面这句等价于 @bot.on('message')
def handle_msg(context):
    group_id = context.get('group_id')
    user_id = context.get('user_id')
    user = group_list.get(group_id, dict()).get(user_id, dict())
    username = user.get('nickname', str(user_id))
    message = UnifiedMessage(from_platform='QQ', from_chat=group_id, from_user=username,
                             message=context.get('raw_message'))
    janus_queue_put_sync(queue, CTBDriver.receive, message)
    return {}  # 返回给 HTTP API 插件，走快速回复途径


def send(to_chat: int, message: UnifiedMessage):
    """
    decorator for send new message
    :return:
    """
    context = dict()
    context['message_type'] = 'group'
    context['message'] = MessageSegment.text(
        message.forward_attrs.from_user + ': ' + message.message)  # TODO finish forward attrs
    context['group_id'] = to_chat
    bot.send(context, context['message'])


CTBDriver.api_lookup['QQ']['send'] = send

##### Other initializations #####

# get group list
group_list: Dict[int, Dict[int, Dict]] = dict()  # Dict[group_id, Dict[member_id, member_info]]


# see https://cqhttp.cc/docs/4.13/#/API?id=响应数据23


##### Janus queue for async loop #####
async def async_coro(async_q):
    """
    Asnyc queue for incoming async call
    :param async_q:
    :return:
    """
    while True:
        func, args, kwargs = await async_q.get()
        if asyncio.iscoroutinefunction(func):
            await func(*args, **kwargs)
        else:
            func(*args, **kwargs)
        async_q.task_done()


def start_janus_queue():
    global queue, loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    queue = janus.Queue(loop=loop)
    loop.create_task(async_coro(queue.async_q))
    loop.run_forever()


t = threading.Thread(target=start_janus_queue)
CTBDriver.threads.append(t)
t.start()


def run():
    bot.run(host=config.get('ListenIP'), port=config.get('ListenPort'))


t = threading.Thread(target=run)
CTBDriver.threads.append(t)
t.start()
