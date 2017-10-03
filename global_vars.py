from command import Command
qq_bot = None
dp = None
tg_bot = None
tg_bot_id = None
command_list = []
group_members = []  # group member dicts in a list, index is forward_index


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
    global command_list
    command_list.append(command)


def set_group_members(_group_members, index=-1):
    """
    set group members list
    :param _group_members: if index == -1, then it's group member dicts in a list in a list(all forwards),
    else just a group member dicts in a list(single forward)
    :param index: forward index
    :return:
    """
    global group_members
    if index >= 0:
        group_members[index] = _group_members
    else:
        group_members = _group_members
