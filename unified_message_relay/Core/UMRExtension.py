from . import UMRLogging
from . import UMRConfig
from typing import List
import importlib

logger = UMRLogging.get_logger('Plugin')


def load_extensions():
    extensions: List = UMRConfig.config.get('Extensions')
    if extensions:
        for e in extensions:
            importlib.import_module(e)

