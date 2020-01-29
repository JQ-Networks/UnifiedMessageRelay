from . import UMRLogging

logger = UMRLogging.getLogger('Plugin')


def load_extensions():
    import Extension


def load_platform_extensions():
    import PlatformExtension
