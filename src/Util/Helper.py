from typing import List, Union, Dict
import logging
from janus import Queue


# test attributes in config.yaml
def check_attribute(config: Dict, attributes: List[str], logger: logging.Logger) -> Union[str, None]:
    """
    Test if attributes exist in config
    :param config: config file
    :param attributes: list of attribute strings
    :param logger: log to this logger
    :return: str for first missing attribute, or None for Okay
    """
    for attr in attributes:
        if attr not in config:
            logger.error(f'{attr} not found in config.yaml')
            exit(-1)
    return None


def check_api(api_lookup, driver_platform, api_name, logger: logging.Logger):
    if driver_platform not in api_lookup:
        logger.error(f'driver for {driver_platform} not exists')
        return False
    if api_name not in api_lookup[driver_platform]:
        logger.error(f'api "{api_name}" for {driver_platform} not exists')
        return False
    return True


# async put new task to janus queue
async def janus_queue_put_async(_janus_queue: Queue, func: callable, *args, **kwargs):
    await _janus_queue.async_q.put((func, args, kwargs))


# sync put new task to janus queue
def janus_queue_put_sync(_janus_queue: Queue, func: callable, *args, **kwargs):
    _janus_queue.sync_q.put((func, args, kwargs))
