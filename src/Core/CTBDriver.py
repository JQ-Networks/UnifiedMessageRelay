from typing import Callable, Dict, List, DefaultDict
from threading import Thread
import janus
from .CTBType import UnifiedMessage
from collections import defaultdict

# region Driver API lookup table
api_lookup: DefaultDict[str, Dict[str, callable]] = defaultdict(dict)
threads: List[Thread] = list()
# endregion

# launch dispatcher
from .CTBDispatcher import dispatch


# region API declaration
async def receive(messsage: UnifiedMessage):
    """
    handler for received message
    this function should be called from driver
    :return:
    """
    await dispatch(messsage)


async def send(to_chat: int, messsage: UnifiedMessage):
    """
    function prototype for send new message
    this function should be implemented in driver, sync or async
    :return:
    """
    pass


async def control():
    """
    function prototype for administrative control
    :return:
    """
    pass

# endregion

import Driver