from typing import Callable, Dict, List
import janus
from .UnifiedMessage import UnifiedMessage

sender = dict()
controller = dict()
threads = list()
janus_queue: Dict[str, janus.Queue] = dict()
run: Callable

from .CTBDispatcher import dispatch


async def receive(messsage: UnifiedMessage):
    """
    handler for received message
    :return:
    """
    await dispatch(messsage)


async def send(to_chat: int, messsage: UnifiedMessage):
    """
    function prototype for send new message
    :return:
    """
    pass


async def control():
    """
    function prototype for administrative control
    :return:
    """
    pass


from . import CTBManager
CONFIG = CTBManager.CONFIG


def load_drivers():
    """
    load all drivers
    :return: None
    """
    import Driver


def set_run_blocking(_run):
    global run
    run = _run
