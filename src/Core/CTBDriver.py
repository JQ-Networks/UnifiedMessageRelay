from typing import Callable, Dict, List, DefaultDict, Union
from threading import Thread
import janus
from .CTBType import UnifiedMessage
from . import CTBLogging
from collections import defaultdict

logger = CTBLogging.getLogger('Driver')

# region Driver API lookup table
api_lookup_table: DefaultDict[str, Dict[str, Callable]] = defaultdict(dict)
threads: List[Thread] = list()


# endregion

# region Driver API for other modules
def api_lookup(driver: str, api: str) -> Union[None, Callable]:
    if driver not in api_lookup_table:
        logger.error(f'driver "{driver}" is not registered')
        return None
    if api not in api_lookup_table[driver]:
        logger.error(f'api "{api}" in {driver} is not registered')
        return None
    return api_lookup_table[driver][api]


def api_register(driver: str, api: str, func: Callable):
    api_lookup_table[driver][api] = func

# endregion

# launch dispatcher
# dispatcher should be launched after declaration of api_lookup
from .CTBDispatcher import dispatch


# region Driver API declaration for SubDriver call
async def receive(messsage: UnifiedMessage):
    """
    handler for received message
    this function should be called from driver
    :return:
    """
    await dispatch(messsage)


# endregion


import Driver
