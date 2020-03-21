"""
Controller of the whole program
"""

from . import UMRLogging
from . import UMRDriver
from . import UMRDispatcher
from . import UMRCommand

import asyncio

from time import sleep
logger = UMRLogging.get_logger('Manager')


class UMRManager:
    @staticmethod
    def run():
        try:
            # init message dispatcher
            UMRDispatcher.init_dispatcher()

            # init driver and other extensions
            from . import UMRExtension
            UMRExtension.load_extensions()

            # init drivers for different platform
            asyncio.run(UMRDriver.init_drivers())

            # block main thread
            for i in UMRDriver.threads:
                i.join()

        except KeyboardInterrupt:
            logger.info('Terminating')
            exit(0)
