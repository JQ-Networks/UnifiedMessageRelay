from command import Command
qq_bot = None
dp = None
tg_bot = None
tg_bot_id = None
command_list = []


def set_qq_bot(_qq_bot):
    global qq_bot
    qq_bot = _qq_bot


def set_dp(_dp):
    global dp
    dp = _dp


def set_tg_bot(_tg_bot):
    global tg_bot
    tg_bot = _tg_bot


def set_tg_bot_id(_tg_bot_id):
    global tg_bot_id
    tg_bot_id = _tg_bot_id


def append_command(command: Command):
    command_list.append(command)
