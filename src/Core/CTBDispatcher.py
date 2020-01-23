from typing import Union, List, DefaultDict
import asyncio
from collections import defaultdict
from janus import Queue
from .CTBType import UnifiedMessage, Action, ActionType
from . import CTBLogging
from .CTBDriver import api_lookup
from .CTBConfig import config
from Util.Helper import janus_queue_put_async, check_attribute, check_api
from threading import Thread

logger = CTBLogging.getLogger('Dispatcher')

# forward graph

action_graph: DefaultDict[str, DefaultDict[int, List[Action]]] = defaultdict(
    lambda: defaultdict(lambda: list()))  # action graph
queue_graph: DefaultDict[str, DefaultDict[int, Union[None, Queue]]] = defaultdict(
    lambda: defaultdict(lambda: None))  # worker queue graph
thread_graph: DefaultDict[str, DefaultDict[int, Union[None, Thread]]] = defaultdict(
    lambda: defaultdict(lambda: None))  # worker thread graph


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
        if i['From'] not in thread_graph and i['FromChat'] not in thread_graph[i['To']]:
            t = generate_worker(i['From'], i['FromChat'])
            thread_graph[i['From']][i['FromChat']] = t
            t.start()
    else:
        logger.warning(f'Unrecognized ForwardType in config: "{i["ForwardType"]}", ignoring')


async def dispatch(message: UnifiedMessage):

    if message.forward_attrs.from_chat not in action_graph[message.forward_attrs.from_platform]:
        logger.debug(
            f'ignoring unrelated message from {message.forward_attrs.from_platform}: {message.forward_attrs.from_chat}')

    for action in action_graph[message.forward_attrs.from_platform][message.forward_attrs.from_chat]:
        # TODO plugin logic
        if action.action_type == ActionType.Reply and not message.forward_attrs.reply_to:
            continue
        # TODO should control action be dispatched here?
        if not check_api(api_lookup, action.to_platform, 'send', logger):
            continue

        await janus_queue_put_async(queue_graph[action.to_platform][action.to_chat],
                                    api_lookup[action.to_platform]['send'], action.to_chat, message)
        logger.debug(f'added new task to ({action.to_platform}, {action.to_chat})')
