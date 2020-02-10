from typing import  Dict, List, Union, Any
from threading import Thread
from .UMRType import UnifiedMessage
from . import UMRLogging
from . import UMRConfig
from asyncio import iscoroutinefunction

logger = UMRLogging.getLogger('Driver')


# region Driver API lookup table
class BaseDriver:
    def send(self, to_chat: int, message: UnifiedMessage):
        pass

    def is_group_admin(self, chat_id: int, user_id: int) -> bool:
        pass

    def is_group_owner(self, chat_id: int, user_id: int) -> bool:
        pass

    def start(self):
        pass

driver_class_lookup_table: Dict[str, Any] = dict()
driver_lookup_table: Dict[str, BaseDriver] = dict()
threads: List[Thread] = list()  # all threads that drivers created


def register_driver(name, driver):
    driver_class_lookup_table[name] = driver

# endregion


# region Driver API for other modules
def driver_lookup(platform: str) -> Union[None, BaseDriver]:
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
        return

    func = getattr(driver, api_name)
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


# TODO initialize driver

import Driver

config = UMRConfig.config.get('Driver')

for driver_name, driver_config in config.items():
    if driver_config['Base'] not in driver_class_lookup_table:
        logger.error(f'Base driver "{driver_config["Base"]}" not found')
        exit(-1)
    driver = driver_class_lookup_table[driver_config['Base']](driver_name)
    driver.start()
    driver_lookup_table[driver_name] = driver




