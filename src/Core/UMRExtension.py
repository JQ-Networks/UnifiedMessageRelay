from . import UMRLogging

logger = UMRLogging.get_logger('Plugin')


def load_extensions():
    import Extension


def load_platform_extensions():
    import PlatformExtension
