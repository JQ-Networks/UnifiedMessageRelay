from typing import Callable, Dict, List, DefaultDict, Union
from threading import Thread
import janus
from .UMRType import UnifiedMessage
from . import UMRLogging
from collections import defaultdict
from asyncio import iscoroutinefunction

logger = UMRLogging.getLogger('Driver')

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
        logger.warn(f'api "{api}" in {driver} is not registered')
        return None
    return api_lookup_table[driver][api]


def api_register(driver: str, api: str, func: Callable):
    api_lookup_table[driver][api] = func


async def api_call(platform: str, api_name: str, *args, **kwargs):
    """
    fast api call
    :param platform: driver platform
    :param api_name: name of the api
    :param args: positional args to pass
    :param kwargs: keyword args to pass
    :return: None for API not found, api result for successful calling
    """
    func = api_lookup(platform, api_name)
    if not func:
        return

    if iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)

# endregion

# launch dispatcher
# dispatcher should be launched after declaration of api_lookup
from .UMRDispatcher import dispatch


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
