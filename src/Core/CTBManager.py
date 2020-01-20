"""
Controller of the whole program
"""
import coloredlogs
import logging
import traceback
import sys
from logging.handlers import RotatingFileHandler
import yaml
import importlib
import os
import pathlib
import threading
import time

from Utils import Helper

CONFIG: dict

class CTBManager:
    __slots__ = [
        'logger',  # output to both file and stdout
        'config',  # loaded config from ~/.ctb/config.yaml
        'driver',  # registered driver instance
        'path',  # src folder path
        'CTBDriver' # CTBDriver reference
    ]

    def __init__(self):
        # init path
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.path = pathlib.Path(dir_path).parent.parent

        # init loggeing
        self.init_logging()

        # init global config
        self.load_config()

        # init drivers for different platform
        self.load_drivers()

        # init plugin hooks
        self.load_plugins()

    def init_logging(self):
        # init coloredlogs
        fmt = '[%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n'
        coloredlogs.install(fmt=fmt, level='DEBUG')

        # get and conf root logger
        root_logger = logging.getLogger('CTB')
        root_logger.setLevel('DEBUG')

        # log main thread
        self.logger = logging.getLogger("CTB.CTBManager")

        def log_except_hook(*exc_info):
            # Output unhandled exception
            ex_hook_logger = root_logger.getChild('Exception')
            text = "".join(traceback.format_exception(*exc_info))
            ex_hook_logger.error("Unhandled exception: %s", text)

        sys.excepthook = log_except_hook

        # set rotate handler
        rotate_handler = RotatingFileHandler(
            'bot.log', maxBytes=1048576, backupCount=3, encoding='utf-8')
        standard_formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(levelname)s] (%(filename)s:%(lineno)d):\n%(message)s\n')
        rotate_handler.setFormatter(standard_formatter)
        root_logger.addHandler(rotate_handler)

    def load_config(self):
        # load config from home directory
        global CONFIG
        try:
            home = str(pathlib.Path.home())
            CONFIG = yaml.load(open(f'{home}/.ctb/config.yaml'))
        except FileNotFoundError:
            self.logger.error(f'config.yaml not found under "{home}/.ctb/"!')
            exit(-1)

        # test attributes
        attributes = [
            'ForwardList',  # Directed graph contains forward relationships
        ]
        Helper.test_attribute(CONFIG, attributes, self.logger)

    def load_drivers(self):
        from . import CTBDriver
        CTBDriver.load_drivers()
        self.CTBDriver = CTBDriver

        required_drivers = set(CONFIG['ForwardList']['Accounts'])
        for driver in required_drivers:
            if driver not in CTBDriver.sender:
                self.logger.error(f'Error: driver for {driver} is not registered')
                exit(-1)

        CTBDriver.load_drivers()

    def load_plugins(self):
        from . import CTBPlugin
        CTBPlugin.load_plugins()

    def build_graph(self):
        from . import CTBDispatcher
        attributes = [
            'From',
            'FromChat',
            'To',
            'ToChat',
            'Type'
        ]
        for i in CONFIG['ForwardList']['Topology']:
            Helper.test_attribute(i, attributes, self.logger)
            if i['From'] not in CTBDispatcher.graph:
                CTBDispatcher.graph[i['From']] = dict()
            if i['FromChat'] not in CTBDispatcher.graph[i['From']]:
                CTBDispatcher.graph[i['From']][i['FromChat']] = list()
            if i['To'] not in CTBDispatcher.graph:
                CTBDispatcher.graph[i['To']] = dict()
            if i['ToChat'] not in CTBDispatcher.graph[i['To']]:
                CTBDispatcher.graph[i['To']][i['ToChat']] = list()
            action_type = CTBDispatcher.ActionType.All
            CTBDispatcher.graph[i['From']][i['FromChat']].append(
                CTBDispatcher.Action(i['To'], i['ToChat'], action_type))
            if i['Type'] == 'BiDirection':
                CTBDispatcher.graph[i['To']][i['ToChat']].append(
                    CTBDispatcher.Action(i['From'], i['FromChat'], action_type))
            elif i['Type'] == 'OneWay':
                pass
            elif i['Type'] == 'AcceptReply':
                action_type = CTBDispatcher.ActionType.Reply
                CTBDispatcher.graph[i['To']][i['ToChat']].append(
                    CTBDispatcher.Action(i['From'], i['FromChat'], action_type))
            else:
                self.logger.warning(f'Unrecognized Type in config: "{i["Type"]}", treated as OneWay')

        CTBDispatcher.set_graph_ready()

    def run(self):
        self.load_drivers()
        self.build_graph()
        time.sleep(1)
        self.CTBDriver.run()
        for i in self.CTBDriver.threads:
            i.join()
        pass
