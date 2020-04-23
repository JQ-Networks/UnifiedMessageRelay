import logging
import coloredlogs
import traceback
import sys
from logging.handlers import RotatingFileHandler
import os
import yaml
import pathlib


# init coloredlogs
__fmt = '[%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n'

# get and conf root logger
__root_logger: logging.Logger = logging.getLogger('UMR')
coloredlogs.install(fmt=__fmt, level='DEBUG')
logging.getLogger('httpx').setLevel(logging.INFO)
logging.getLogger('aiogram').setLevel(logging.INFO)

# coloredlogs.install(fmt=__fmt, level='DEBUG', logger=__root_logger)
# coloredlogs.install(fmt=__fmt, level='DEBUG', logger=logging.getLogger('Mirai-core'))
# coloredlogs.install(fmt=__fmt, level='DEBUG', logger=logging.getLogger('aiogram'))

# Logger for this module
logger = __root_logger.getChild('Logging')


def get_logger(suffix):
    return __root_logger.getChild(suffix)


def __log_except_hook(*exc_info):
    # Output unhandled exception
    ex_hook_logger = __root_logger.getChild('UnknownException')
    text = "".join(traceback.format_exception(*exc_info))
    ex_hook_logger.error("Unhandled exception: %s", text)


home = str(pathlib.Path.home())


try:
    config = yaml.load(open(f'{home}/.umr/config.yaml'), Loader=yaml.FullLoader)

    # test attributes
    attributes = [
        ('LogRoot', True, '/var/log/umr'),
        ('Debug', True, True)           # verbose output
    ]
    from ..Util.Helper import check_attribute

    check_attribute(config, attributes, logger)
    debug = config.get('Debug')

    # log level
    if debug:
        debug_level = 'DEBUG'
    else:
        debug_level = 'INFO'
    __root_logger.setLevel(debug_level)

    # log to file
    log_path = config['LogRoot']
    if log_path.startswith('~'):
        log_path = f'{home}/{config["LogRoot"][1:]}'

    # set rotate handler
    os.makedirs(log_path, exist_ok=True)  # create logging folder
    __rotate_handler = RotatingFileHandler(
        os.path.join(log_path, 'bot.log'), maxBytes=1048576, backupCount=1, encoding='utf-8')
    __standard_formatter = logging.Formatter(
        '[%(asctime)s][%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n')
    __rotate_handler.setFormatter(__standard_formatter)
    # __root_logger.addHandler(__rotate_handler)
    logging.getLogger().addHandler(__rotate_handler)

except FileNotFoundError:
    logger.error(f'config.yaml not found under "{home}/.umr/"!')
    exit(-1)
