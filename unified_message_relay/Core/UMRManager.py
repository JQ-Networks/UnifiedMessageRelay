"""
Controller of the whole program
"""

from . import UMRLogging
from . import UMRConfig
from . import UMRDispatcher
from . import UMRDriver
from . import UMRExtension
import asyncio

from time import sleep
logger = UMRLogging.get_logger('Manager')


class UMRManager:
    @staticmethod
    def run():
        try:
            # init logging to file
            UMRLogging.post_init()

            # init message dispatcher
            UMRDispatcher.init_dispatcher()

            # init driver and other extensions
            UMRConfig.load_extensions()

            # reload config
            UMRConfig.reload_config()

            # init drivers for different platform
            asyncio.run(UMRDriver.init_drivers())

            # init extensions after driver is available
            asyncio.run(UMRExtension.post_init())

            # block main thread
            for i in UMRDriver.threads:
                i.join()

        except KeyboardInterrupt:
            logger.info('Terminating')
            exit(0)
