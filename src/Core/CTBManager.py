"""
Controller of the whole program
"""

from . import CTBLogging
from . import CTBConfig
from . import CTBDriver

from time import sleep
logger = CTBLogging.getLogger('Manager')


class CTBManager:
    @staticmethod
    def check_drivers():
        required_drivers = set(CTBConfig.config['ForwardList']['Accounts'])
        for driver in required_drivers:
            if driver not in CTBDriver.api_lookup:
                logger.error(f'Error: driver for {driver} is not registered')
                exit(-1)

    @staticmethod
    def load_plugins():
        from . import CTBExtension
        CTBExtension.load_platform_extensions()
        CTBExtension.load_extensions()

    @staticmethod
    def run():
        # init drivers for different platform
        CTBManager.check_drivers()
        sleep(2)
        # init plugin hooks
        CTBManager.load_plugins()
        for i in CTBDriver.threads:
            i.join()
        # TODO check if stop should be handled
        pass
