import sys
from main.command import Command
from main.DaemonClass import Daemon
from main.message_persistence import MessageDB
from main.file_persistence import FileDB
import telegram

daemon: Daemon = None
qq_bot = None
dp = None
mdb: MessageDB = None
fdb: FileDB = None
tg_bot: telegram.Bot = None
tg_bot_id: int = None
command_list = []
group_members = [[]]


def append_command(command: Command):
    global command_list
    command_list.append(command)


def create_variable(name, var):
    this_module = sys.modules[__name__]
    setattr(this_module, name, var)
