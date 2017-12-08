import global_vars


class Command:
    def __init__(self, command, cmd, handler, require_admin, tg_only, qq_only, description):
        self.command = command
        self.cmd = cmd
        self.handler = handler  # handler: function(forward_index, tg_group_id, qq_group_id)
        self.require_admin = require_admin
        self.tg_only = tg_only  # if True, handler becomes function(tg_group_id)
        self.qq_only = qq_only  # if True, handler becomes function(qq_group_id)
        self.description = description


def command_listener(command, short_command='', require_admin=False, tg_only=False, qq_only=False, description=''):
    def decorator(handler):
        global_vars.append_command(Command(command, short_command, handler, require_admin, tg_only, qq_only, description))
        global_vars.create_variable(handler.__name__, handler)  # add command to global_vars, for cross-plugin access
        return handler
    return decorator
