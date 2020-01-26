from typing import Dict, List, Union
from asyncio import iscoroutinefunction
from . import UMRConfig
from . import UMRLogging
from .UMRType import UnifiedMessage, Command, ForwardAttributes, MessageEntity
from .UMRMessageHook import register_hook
from .UMRDriver import api_lookup

logger = UMRLogging.getLogger('Command')

command_map: Dict[str, Command] = dict()
command_start: str = UMRConfig.config['CommandStart']


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
    logger.debug(f'dispatching command: "{cmd}" with args: "{" ".join(args)}"')
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


def register_command(cmd: Union[str, List[str]] = '', description: str = '', platform: str = ''):
    """
    register command
    :param cmd: command keyword, must not be null
    :param description: command description, will show in help command
    :param platform: platform name, if specified, only message from that platform will trigger this command
    :return:
    """

    def deco(func):
        if isinstance(cmd, str):
            assert cmd not in command_map, f'Error, "{cmd}" has been registered'
            command_map[cmd] = Command(platform=platform, description=description, command_function=func)
        else:
            for c in cmd:
                assert c not in command_map, f'Error, "{c}" has been registered'
                command_map[c] = Command(platform=platform, description=description, command_function=func)
        return func

    return deco


@register_command(cmd='help', description='get list of commands')
async def command(forward_attrs: ForwardAttributes, args: List):
    """
    Prototype of command
    :param forward_attrs:
    :param args:
    :return:
    """
    if args:  # args should be empty
        return

    send = api_lookup(forward_attrs.from_platform, 'send')
    if not send:
        return

    message = UnifiedMessage()

    help_text = 'Available commands in this group:'
    message.message.append(MessageEntity(text=help_text))
    for cmd, cmd_obj in command_map.items():
        if cmd_obj.platform and cmd_obj.platform != forward_attrs.from_platform:
            continue
        message.message.append(MessageEntity(text='\n' + cmd + ': ', entity_type='bold'))
        message.message.append(MessageEntity(text=cmd_obj.description))

    if iscoroutinefunction(send):
        await send(forward_attrs.from_chat, message)
    else:
        send(forward_attrs.from_chat, message)
