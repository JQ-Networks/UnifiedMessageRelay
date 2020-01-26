from typing import Union, List, DefaultDict, Tuple
import asyncio
from collections import defaultdict
from janus import Queue
from .CTBType import UnifiedMessage, Action, ActionType, MessageHook
from . import CTBLogging
from .CTBDriver import api_lookup
from .CTBConfig import config
from .CTBMessageHook import message_hook_src, message_hook_full
from Util.Helper import janus_queue_put_async, check_attribute
from threading import Thread

logger = CTBLogging.getLogger('Dispatcher')

# forward graph

action_graph: DefaultDict[str, DefaultDict[int, List[Action]]] = defaultdict(
    lambda: defaultdict(lambda: list()))  # action graph
queue_graph: DefaultDict[str, DefaultDict[int, Union[None, Queue]]] = defaultdict(
    lambda: defaultdict(lambda: None))  # worker queue graph
thread_graph: DefaultDict[str, DefaultDict[int, Union[None, Thread]]] = defaultdict(
    lambda: defaultdict(lambda: None))  # worker thread graph


##### initialize workers #####

def generate_worker(to_platform: str, to_chat: int):
    def worker():
        async def async_coro(async_q):
            """
            Asnyc queue for incoming async call
            :param async_q:
            :return:
            """
            while True:
                func, args, kwargs = await async_q.get()
                logger.debug(f'({to_platform}, {to_chat}): got new task')
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
                async_q.task_done()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue = Queue(loop=loop)
        loop.create_task(async_coro(queue.async_q))
        global queue_graph
        queue_graph[to_platform][to_chat] = queue
        loop.run_forever()

    thread = Thread(target=worker)
    return thread


attributes = [
    'From',
    'FromChat',
    'To',
    'ToChat',
    'ForwardType'
]
for i in config['ForwardList']['Topology']:
    check_attribute(i, attributes, logger)

    # Add action
    # BiDirection = two ALL
    # OneWay      = one All
    # ReplyOnly = one Reply

    # init forward graph and workers
    if i['ForwardType'] == 'BiDirection':
        action_type = ActionType.All
        action_graph[i['From']][i['FromChat']].append(
            Action(i['To'], i['ToChat'], action_type))
        action_graph[i['To']][i['ToChat']].append(
            Action(i['From'], i['FromChat'], action_type))
        # init worker
        if i['To'] not in thread_graph and i['ToChat'] not in thread_graph[i['To']]:
            t = generate_worker(i['To'], i['ToChat'])
            thread_graph[i['To']][i['ToChat']] = t
            t.start()
        if i['From'] not in thread_graph and i['FromChat'] not in thread_graph[i['To']]:
            t = generate_worker(i['From'], i['FromChat'])
            thread_graph[i['From']][i['FromChat']] = t
            t.start()
    elif i['ForwardType'] == 'OneWay':
        action_type = ActionType.All
        action_graph[i['From']][i['FromChat']].append(
            Action(i['To'], i['ToChat'], action_type))
        # init worker
        if i['To'] not in thread_graph and i['ToChat'] not in thread_graph[i['To']]:
            t = generate_worker(i['To'], i['ToChat'])
            thread_graph[i['To']][i['ToChat']] = t
            t.start()
    elif i['ForwardType'] == 'ReplyOnly':
        action_type = ActionType.Reply
        action_graph[i['From']][i['FromChat']].append(
            Action(i['To'], i['ToChat'], action_type))
        # init worker
        if i['To'] not in thread_graph and i['ToChat'] not in thread_graph[i['To']]:
            t = generate_worker(i['To'], i['ToChat'])
            thread_graph[i['To']][i['ToChat']] = t
            t.start()
    else:
        logger.warning(f'Unrecognized ForwardType in config: "{i["ForwardType"]}", ignoring')


##### core dispatcher #####

async def dispatch(message: UnifiedMessage):
    if message.forward_attrs.from_chat not in action_graph[message.forward_attrs.from_platform]:
        logger.debug(
            f'ignoring unrelated message from {message.forward_attrs.from_platform}: {message.forward_attrs.from_chat}')

    # hook for matching source only
    for hook in message_hook_src:
        if (not hook.src_driver or hook.src_driver == message.forward_attrs.from_platform) and \
                (not hook.src_chat or hook.src_chat == message.forward_attrs.from_chat):
            if await hook.hook_function(message):
                return

    for action in action_graph[message.forward_attrs.from_platform][message.forward_attrs.from_chat]:

        # hook for matching all four attributes
        for hook in message_hook_full:
            if (not hook.src_driver or hook.src_driver == message.forward_attrs.from_platform) and \
                    (not hook.src_chat or hook.src_chat == message.forward_attrs.from_chat) and \
                    (not hook.dst_driver or hook.dst_driver == action.to_platform) and \
                    (not hook.dst_chat or hook.dst_chat == action.to_chat):
                if hook.hook_function(action.to_platform, action.to_chat, message):
                    continue

        # basic message filtering
        if action.action_type == ActionType.Reply and not message.forward_attrs.reply_to:
            continue

        # check api registration
        api_send = api_lookup(action.to_platform, 'send')
        if not api_send:
            continue

        await janus_queue_put_async(queue_graph[action.to_platform][action.to_chat],
                                    api_send, action.to_chat, message)
        logger.debug(f'added new task to ({action.to_platform}, {action.to_chat})')
