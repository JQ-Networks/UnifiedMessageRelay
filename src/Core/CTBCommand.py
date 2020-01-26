from typing import Dict
from . import CTBConfig
from . import CTBLogging
from .CTBType import UnifiedMessage, Command
from .CTBMessageHook import register_hook

logger = CTBLogging.getLogger('Command')

command_map: Dict[str, Command] = dict()
command_start: str = CTBConfig.config['CommandStart']


@register_hook()
async def command_dispatcher(message: UnifiedMessage):
    # filter command
    if len(message.message) == 0:  # command must have some texts
        return False

    msg = assemble_message(message)

    if not msg.startswith(command_start):  # command must start with command_start
        return False

    cmd, *args = msg.split(' ')
    cmd = cmd[2:]
    if cmd in command_map:
        # check if platform matches
        if command_map[cmd].platform and command_map[cmd].platform != message.forward_attrs.from_platform:
            return False

        await command_map[cmd].command_function(message.forward_attrs, args)
        return True
    else:
        return False


def assemble_message(message: UnifiedMessage) -> str:
    """
    assemble text of the message to a single string
    :param message: UnifiedMessage to assemble
    :return: result string
    """
    return ''.join(map(lambda x: x.text, message.message))


def register_command(cmd: str = '', platform: str = ''):
    """
    register command
    :param cmd: command keyword, must not be null
    :param platform: platform name, if specified, only message from that platform will trigger this command
    :return:
    """

    def deco(func):
        assert cmd not in command_map, f'Error, "{cmd}" has been registered'
        command_map[cmd] = Command(platform=platform, command_function=func)
        return func

    return deco
