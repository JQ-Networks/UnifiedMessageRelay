from typing import Dict, List, Union, Set
from asyncio import iscoroutinefunction
from . import UMRConfig
from . import UMRLogging
from .UMRType import UnifiedMessage, Command, ChatAttribute, MessageEntity, ChatType, Privilege, SendAction, EntityType
from .UMRMessageHook import register_hook
from .UMRDriver import api_call
from .UMRAdmin import is_bot_admin, is_group_admin, is_group_owner
from Util.Helper import unparse_entities_to_markdown

logger = UMRLogging.getLogger('Command')

command_map: Dict[str, Command] = dict()
command_start: str = UMRConfig.config['CommandPrefix']


async def unauthorized(chat_attrs: ChatAttribute, required_privilege: Privilege):
    privilege_names = {
        Privilege.GROUP_ADMIN: 'Group Admin',
        Privilege.GROUP_OWNER: 'Group Owner',
        Privilege.BOT_ADMIN:   'Bot Admin'
    }

    error_message = f'Unauthorized command, requires {privilege_names[required_privilege]}'
    await quick_reply(chat_attrs, error_message)


@register_hook()
async def command_dispatcher(message: UnifiedMessage):
    # filter command
    if len(message.message) == 0:  # command must have some texts
        return False

    msg = unparse_entities_to_markdown(message, EntityType.PLAIN)

    if not msg.startswith(command_start):  # command must start with command_start
        return False

    cmd, *args = msg.split(' ')
    cmd = cmd[len(command_start):]
    logger.debug(f'dispatching command: "{cmd}" with args: "{" ".join(args)}"')
    if cmd in command_map:
        # check if platform matches
        if command_map[cmd].platform:
            base_platform = UMRConfig.config['Driver'][message.chat_attrs.platform]['Base']
            if base_platform not in command_map[cmd].platform:
                return False

        # filter chat_type
        if command_map[cmd].chat_type:
            if message.chat_attrs.chat_id > 0 and command_map[cmd].chat_type == ChatType.GROUP:
                return False
            if message.chat_attrs.chat_id < 0 and command_map[cmd].chat_type == ChatType.PRIVATE:
                return False

        # filter privilege
        if command_map[cmd].privilege:
            if command_map[cmd].privilege == Privilege.BOT_ADMIN:
                if not await is_bot_admin(message.chat_attrs.platform, message.chat_attrs.user_id):
                    await unauthorized(message.chat_attrs, command_map[cmd].privilege)
                    return True
            elif command_map[cmd].privilege == Privilege.GROUP_OWNER:
                if not await is_bot_admin(message.chat_attrs.platform, message.chat_attrs.user_id) or \
                        not await is_group_owner(platform=message.chat_attrs.platform,
                                                 chat_id=message.chat_attrs.chat_id,
                                                 chat_type=message.chat_attrs.chat_type,
                                                 user_id=message.chat_attrs.user_id):
                    await unauthorized(message.chat_attrs, command_map[cmd].privilege)
                    return True
            elif command_map[cmd].privilege == Privilege.GROUP_ADMIN:
                if not await is_bot_admin(message.chat_attrs.platform, message.chat_attrs.user_id) or \
                        not await is_group_admin(platform=message.chat_attrs.platform,
                                                 chat_id=message.chat_attrs.chat_id,
                                                 chat_type=message.chat_attrs.chat_type,
                                                 user_id=message.chat_attrs.user_id):
                    await unauthorized(message.chat_attrs, command_map[cmd].privilege)
                    return True

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
    help_text = 'Available commands in this group: '
    message = help_text
    for cmd, cmd_obj in command_map.items():
        if cmd_obj.platform and chat_attrs.platform not in cmd_obj.platform:
            continue
        message += '\n'
        cmd_text = cmd + ': '
        message_entities.append(
            MessageEntity(start=len(message),
                          end=len(message) + len(cmd_text),
                          entity_type=EntityType.BOLD))
        message_entities += cmd_text
        message_entities += cmd_obj.description

    await quick_reply(chat_attrs, message, message_entities)


async def quick_reply(chat_attrs: ChatAttribute, text: str, message_entities: List[MessageEntity] = None):
    """
    send quick reply for bot commands
    :param chat_attrs:
    :param text:
    :param message_entities:
    :return:
    """

    message = UnifiedMessage()
    message.message = text
    message.message_entities = message_entities
    message.send_action = SendAction(message_id=chat_attrs.message_id, user_id=chat_attrs.user_id)

    await api_call(chat_attrs.platform, 'send', chat_attrs.chat_id, chat_attrs.chat_type, message)
