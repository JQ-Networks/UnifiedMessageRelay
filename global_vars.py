import sys
from main.command import Command
import telegram
qq_bot = None
dp = None
tg_bot: telegram.Bot = None
tg_bot_id: int = None
command_list = []


def append_command(command: Command):
    global command_list
    command_list.append(command)


def create_variable(name, var):
    this_module = sys.modules[__name__]
    setattr(this_module, name, var)
