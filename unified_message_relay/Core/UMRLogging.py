import logging
import coloredlogs
import traceback
from logging.handlers import RotatingFileHandler
import os
import pathlib


# init coloredlogs
__fmt = '[%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n'

# get and conf root logger
root_logger: logging.Logger = logging.getLogger('UMR')
coloredlogs.install(fmt=__fmt, level='DEBUG')


def __log_except_hook(*exc_info):
    # Output unhandled exception
    ex_hook_logger = root_logger.getChild('UnknownException')
    text = "".join(traceback.format_exception(*exc_info))
    ex_hook_logger.error("Unhandled exception: %s", text)


def get_logger(suffix):
    return root_logger.getChild(suffix)


def post_init():
    # Logger for this module

    logger = root_logger.getChild('Logging')
    logger.info('Initializing logging')

    from .UMRConfig import config

    # log level
    if '*' in config.LogLevel:
        root_logger.setLevel(f"{config.LogLevel['*']}")
    for logger_name in config.LogLevel:
        if logger_name == '*':
            continue
        logging.getLogger(logger_name).setLevel(f"{config.LogLevel[logger_name]}")

    # log to file
    log_path = config.LogRoot
    if log_path.startswith('~'):
        home = str(pathlib.Path.home())
        log_path = f'{home}/{config.LogRoot[1:]}'

    # set rotate handler
    os.makedirs(log_path, exist_ok=True)  # create logging folder
    rotate_handler = RotatingFileHandler(
        os.path.join(log_path, 'bot.log'), maxBytes=1048576, backupCount=1, encoding='utf-8')
    standard_formatter = logging.Formatter(
        '[%(asctime)s][%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n')
    rotate_handler.setFormatter(standard_formatter)
    # __root_logger.addHandler(__rotate_handler)
    logging.getLogger().addHandler(rotate_handler)

    logger.info('Initialized logging')
