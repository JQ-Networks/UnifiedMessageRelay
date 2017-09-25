class Command:
    def __init__(self, command, handler, require_admin):
        self.command = command
        self.handler = handler  # handler: function(forward_index, tg_group_id, qq_group_id)
        self.require_admin = require_admin


def command_listener(self, command, require_admin=False):
    def decorator(handler):
        self.command_list.append(Command(command, handler, require_admin))
    return decorator
