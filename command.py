import global_vars
import logging
from functools import wraps


logger = logging.getLogger("CTBMain." + __name__)


class Command:
    def __init__(self,
                 command: str,
                 short_command: str,
                 handler: callable,
                 require_admin: bool,
                 tg_only: bool,
                 qq_only: bool,
                 description: str):
        """
        Command class, used to store commands
        :param command: full command
        :param short_command: abbreviation of the command
        :param handler: function of command handler
        :param require_admin: if the command is admin only (not implemented)
        :param tg_only: if the command is only available on telegram side
        :param qq_only: if the command is only available on QQ side
        :param description: description of the command, will show in !!show commands
        """

        self.command = command
        self.short_command = short_command
        self.handler = handler  # handler: function(forward_index, tg_group_id, qq_group_id)
        self.require_admin = require_admin
        self.tg_only = tg_only  # if True, handler becomes function(tg_group_id)
        self.qq_only = qq_only  # if True, handler becomes function(qq_group_id)
        self.description = description


def command_listener(command: str,
                     short_command: str='',
                     require_admin: bool=False,
                     tg_only: bool=False,
                     qq_only: bool=False,
                     description: str=''):
    """
    Command decorator, used to register commands
    :param command: full command
    :param short_command: abbreviation of the command
    :param require_admin: if the command is admin only (not implemented)
    :param tg_only: if the command is only available on telegram side
    :param qq_only: if the command is only available on QQ side
    :param description: description of the command, will show in !!show commands
    """

    def decorator(handler):
        logger.debug('Registering new command: ' + command + '(' + handler.__name__ + ')')

        @wraps(handler)
        def return_wrapper(*args, **kwargs):
            logger.debug(command + '(' + handler.__name__ + ')' + ' called')
            return handler(*args, **kwargs)

        global_vars.append_command(Command(command,
                                           short_command,
                                           return_wrapper,
                                           require_admin,
                                           tg_only,
                                           qq_only,
                                           description))

        # add command to global_vars, for cross-plugin access
        global_vars.create_variable(handler.__name__,
                                    return_wrapper)
        logger.debug(command + '(' + handler.__name__ + ') added to global_vars')
        return return_wrapper
    return decorator
