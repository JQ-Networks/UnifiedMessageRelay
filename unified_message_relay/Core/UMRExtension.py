from . import UMRLogging
from . import UMRConfig
from typing import List
import asyncio

__ALL__ = [
    'BaseExtension',
    'register_extension',
    'post_init'
]

logger = UMRLogging.get_logger('Plugin')


class BaseExtension:
    def __init__(self):
        """
        Pre init logic, registering config validator, etc.
        During this stage, only basic config is available, every other function is not up yet.
        """
        pass

    async def post_init(self):
        """
        Real init logic, complete everything else here
        During this stage, the dispatcher and drivers are up and running. Any patch should happen here.
        :return:
        """
        pass


extensions: List[BaseExtension] = []


def register_extension(extension):
    """
    Register extension

    :param extension: extension class instances
    """
    extensions.append(extension)


async def post_init():
    """
    Call every post init method

    """
    if extensions:
        await asyncio.wait([i.post_init() for i in extensions])
