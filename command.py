import global_vars


class Command:
    def __init__(self, command, handler, require_admin, tg_only, qq_only):
        self.command = command
        self.handler = handler  # handler: function(forward_index, tg_group_id, qq_group_id)
        self.require_admin = require_admin
        self.tg_only = tg_only  # if True, handler becomes function(tg_group_id)
        self.qq_only = qq_only  # if True, handler becomes function(qq_group_id)


def command_listener(command, require_admin=False, tg_only=False, qq_only=False):
    def decorator(handler):
        global_vars.append_command(Command(command, handler, require_admin, tg_only, qq_only))
    return decorator
