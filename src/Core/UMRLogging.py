import logging
import coloredlogs
import traceback
import sys
from logging.handlers import RotatingFileHandler
import os
from . import UMRConfig

debug = UMRConfig.config.get('Debug')

if debug:
    debug_level = 'DEBUG'
else:
    debug_level = 'INFO'

# init coloredlogs
__fmt = '[%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n'
coloredlogs.install(fmt=__fmt, level=debug_level)

# get and conf root logger
__root_logger: logging.Logger = logging.getLogger('UMR')
__root_logger.setLevel(debug_level)

# log main thread
__logger: logging.Logger = __root_logger.getChild("Logging")


def __log_except_hook(*exc_info):
    # Output unhandled exception
    ex_hook_logger = __root_logger.getChild('UnknownException')
    text = "".join(traceback.format_exception(*exc_info))
    ex_hook_logger.error("Unhandled exception: %s", text)


sys.excepthook = __log_except_hook

# set rotate handler
os.makedirs('/var/log/umr', exist_ok=True)  # create logging folder
__rotate_handler = RotatingFileHandler(
    '/var/log/umr/bot.log', maxBytes=1048576, backupCount=1, encoding='utf-8')
__standard_formatter = logging.Formatter(
    '[%(asctime)s][%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n')
__rotate_handler.setFormatter(__standard_formatter)
__root_logger.addHandler(__rotate_handler)


def getLogger(suffix):
    return __root_logger.getChild(suffix)
