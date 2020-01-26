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
    def check_drivers():
        required_drivers = set(UMRConfig.config['ForwardList']['Accounts'])
        for driver in required_drivers:
            if driver not in UMRDriver.api_lookup_table:
                logger.error(f'Error: driver for {driver} is not registered')
                exit(-1)

    @staticmethod
    def load_plugins():
        from . import UMRExtension
        UMRExtension.load_platform_extensions()
        UMRExtension.load_extensions()

    @staticmethod
    def run():
        # init drivers for different platform
        UMRManager.check_drivers()
        sleep(2)
        # init plugin hooks
        UMRManager.load_plugins()
        for i in UMRDriver.threads:
            i.join()
        # TODO check if stop should be handled
        pass
