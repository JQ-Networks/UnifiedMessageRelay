from typing import Dict, List, Union, Set
from asyncio import iscoroutinefunction
from . import UMRConfig
from . import UMRLogging
from .UMRType import UnifiedMessage, Command, ChatAttribute, MessageEntity, ChatType, Privilege, SendAction
from .UMRMessageHook import register_hook
from .UMRDriver import api_call, api_lookup
from .UMRAdmin import is_bot_admin
from Util.Helper import assemble_message

logger = UMRLogging.getLogger('Command')

command_map: Dict[str, Command] = dict()
command_start: str = UMRConfig.config['CommandStart']


async def unauthorized(platform, chat_id, required_privilege):
    if not api_lookup(platform, 'send'):
        return
    message = UnifiedMessage()
    privilege_names = {
        Privilege.GROUP_ADMIN: 'Group Admin',
        Privilege.GROUP_OWNER: 'Group Owner',
        Privilege.BOT_ADMIN:   'Bot Admin'
    }
    message.message.append(MessageEntity(text=f'Unauthorized command, requires {privilege_names[required_privilege]}'))

    await api_call(platform, 'send', chat_id, message)


@register_hook()
async def command_dispatcher(message: UnifiedMessage):
    # filter command
    if len(message.message) == 0:  # command must have some texts
        return False

    msg = assemble_message(message)

    if not msg.startswith(command_start):  # command must start with command_start
        return False

    cmd, *args = msg.split(' ')
    cmd = cmd[len(command_start):]
    logger.debug(f'dispatching command: "{cmd}" with args: "{" ".join(args)}"')
    if cmd in command_map:
        # check if platform matches
        if command_map[cmd].platform and message.chat_attrs.platform not in command_map[cmd].platform:
            return False

        # filter chat_type
        if command_map[cmd].chat_type:
            if message.chat_attrs.chat_id > 0 and command_map[cmd].chat_type == ChatType.GROUP:
                return False
            if message.chat_attrs.chat_id < 0 and command_map[cmd].chat_type == ChatType.PRIVATE_CHAT:
                return False

        # filter privilege
        if command_map[cmd].privilege:
            if command_map[cmd].privilege == Privilege.BOT_ADMIN:
                if not is_bot_admin(message.chat_attrs.platform, message.chat_attrs.user_id):
                    await unauthorized(message.chat_attrs.platform, message.chat_attrs.chat_id,
                                       command_map[cmd].privilege)
                    return True
            elif command_map[cmd].privilege == Privilege.GROUP_OWNER:
                pass  # TODO driver API implementation
            elif command_map[cmd].privilege == Privilege.GROUP_ADMIN:
                pass

        await command_map[cmd].command_function(message.chat_attrs, args)
        return True
    else:
        return False


def register_command(cmd: Union[str, List[str]] = '', description: str = '', platform: Union[str, List[str]] = '',
                     chat_type=ChatType.UNSPECIFIED, privilege=''):
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
            command_map[cmd] = Command(platform=platform, description=description, chat_type=chat_type,
                                       privilege=privilege, command_function=func)
        else:
            _cmd = Command(platform=platform, description=description, chat_type=chat_type,
                           privilege=privilege, command_function=func)
            for c in cmd:
                assert c not in command_map, f'Error, "{c}" has been registered'
                command_map[c] = _cmd
        return func

    return deco


@register_command(cmd='help', description='get list of commands')
async def command(chat_attrs: ChatAttribute, args: List):
    """
    Prototype of command
    :param chat_attrs:
    :param args:
    :return:
    """
    if args:  # args should be empty
        return

    message_entities = list()
    help_text = 'Available commands in this group:'
    message_entities.append(MessageEntity(text=help_text))
    for cmd, cmd_obj in command_map.items():
        if cmd_obj.platform and chat_attrs.platform not in cmd_obj.platform:
            continue
        message_entities.append(MessageEntity(text='\n' + cmd + ': ', entity_type='bold'))
        message_entities.append(MessageEntity(text=cmd_obj.description))

    await quick_reply(chat_attrs, message_entities)


async def quick_reply(chat_attrs: ChatAttribute, text: Union[str, List[MessageEntity]]):
    """
    send quick reply for bot commands
    :param chat_attrs:
    :param text:
    :return:
    """

    if not api_lookup(chat_attrs.platform, 'send'):
        return
    message = UnifiedMessage()
    if isinstance(text, str):
        message.message.append(MessageEntity(text=text))
    else:
        message.message = text
    message.send_action = SendAction(message_id=chat_attrs.message_id, user_id=chat_attrs.user_id)

    await api_call(chat_attrs.platform, 'send', chat_attrs.chat_id, message)
