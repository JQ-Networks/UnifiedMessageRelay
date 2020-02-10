"""
Controller of the whole program
"""

from . import UMRLogging
from . import UMRConfig
from . import UMRDriver
from . import UMRCommand

from time import sleep
logger = UMRLogging.getLogger('Manager')


class UMRManager:

    @staticmethod
    def load_plugins():
        from . import UMRExtension
        UMRExtension.load_platform_extensions()
        UMRExtension.load_extensions()

    @staticmethod
    def run():
        try:
            # init drivers for different platform
            sleep(2)
            # init plugin hooks
            UMRManager.load_plugins()
            for i in UMRDriver.threads:
                i.join()
            # TODO check if stop should be handled
            pass
        except KeyboardInterrupt:
            logger.info('Terminating')
            exit(0)
