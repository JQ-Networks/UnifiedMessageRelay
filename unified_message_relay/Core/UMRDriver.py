from typing import Dict, List, Union, Any
from threading import Thread
from .UMRType import UnifiedMessage, ChatType
from . import UMRLogging
from . import UMRConfig
from asyncio import iscoroutinefunction
from . import UMRDispatcher
import asyncio
import importlib

logger = UMRLogging.get_logger('Driver')


# region Driver API lookup table
class BaseDriverMixin:
    def __init__(self, name):
        """
        Create driver instance

        :param name: the name in ForwardList
        """
        pass

    async def post_init(self):
        pass

    async def send(self, to_chat: Union[int, str], chat_type: ChatType, message: UnifiedMessage):
        pass

    async def is_group_admin(self, chat_id: int, chat_type: ChatType, user_id: int) -> bool:
        pass

    async def is_group_owner(self, chat_id: int, chat_type: ChatType, user_id: int) -> bool:
        pass

    def start(self):
        """
        should be non blocking, run everything in new thread and register that thread
        """
        pass

    @property
    def started(self):
        """
        indicator for driver start up progress
        :return: False for not ready, True for ready
        """
        return True

    async def receive(self, message: UnifiedMessage):
        """
        send unified message to dispatch
        this function should not be override
        :param message: unified message to dispatch
        """
        await UMRDispatcher.dispatch(message)


driver_class_lookup_table: Dict[str, Any] = dict()  # driver prototypes
driver_lookup_table: Dict[str, BaseDriverMixin] = dict()  # driver instances
threads: List[Thread] = list()  # all threads that drivers created


def register_driver(name: str, driver_prototype):
    """
    register a driver class
    :param name: driver name, should be global unique
    :param driver_prototype: driver constructor
    """
    driver_class_lookup_table[name] = driver_prototype

# endregion


# region Driver API for other modules
def driver_lookup(platform: str) -> Union[None, BaseDriverMixin]:
    """
    get driver instance
    :param platform: platform name (from config)
    :return: driver instance
    """
    if platform not in driver_lookup_table:
        logger.error(f'Base driver "{platform}" not found')
        return None
    else:
        return driver_lookup_table[platform]


async def api_call(platform: str, api_name: str, *args, **kwargs):
    """
    fast api call
    :param platform: driver alias
    :param api_name: name of the api
    :param args: positional args to pass
    :param kwargs: keyword args to pass
    :return: None for API not found, api result for successful calling
    api result can be any or asyncio.Future, for Future type use result.result() to get the actual result
    """
    driver = driver_lookup(platform)
    if not driver:
        logger.error(f'Due to driver "{platform}" not found, "{api_name}" is ignored')
        return

    func = getattr(driver, api_name)
    if not func:
        return

    if iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)

# endregion


async def __post_init(driver_name):
    wait_count = 60
    while wait_count > 0:
        if driver_lookup_table[driver_name].started:
            await driver_lookup_table[driver_name].post_init()
            break
        await asyncio.sleep(1)
        wait_count -= 1
    logger.error(f'Waiting for {driver_name} to start timed out, unable to execute post-init')


async def init_drivers():
    """
    bring up all the drivers
    this function should be called by UMRManager
    :return:
    """
    config = UMRConfig.config.Driver

    for driver_name, driver_config in config.items():
        if driver_config.Base not in driver_class_lookup_table:
            logger.error(f'Base driver "{driver_config.Base}" not found')
            exit(-1)
        driver: BaseDriverMixin = driver_class_lookup_table[driver_config.Base](driver_name)
        driver.start()
        driver_lookup_table[driver_name] = driver

    loop = asyncio.get_event_loop()

    for driver_name in config.keys():
        asyncio.run_coroutine_threadsafe(__post_init(driver_name), loop)





