import yaml
import pathlib
import os
from typing import Dict, List
from Core import UMRLogging
from Core.UMRMessageHook import register_hook
from Core.UMRCommand import register_command, quick_reply
from Core.UMRType import UnifiedMessage, ChatAttribute, Privilege
from Util.Helper import assemble_message

logger = UMRLogging.getLogger('Plugin.WaterMeter')

home = str(pathlib.Path.home())
yaml_config_dir = f'{home}/.umr/watermeter.yaml'
if os.path.isfile(yaml_config_dir):
    config: Dict[str, List] = yaml.load(open(f'{home}/.umr/watermeter.yaml'),
                                        Loader=yaml.FullLoader)
else:
    config: Dict[str, List] = dict()

if 'Keyword' not in config:
    config['Keyword'] = list()
if 'ChatID' not in config:
    config['ChatID'] = list()


# Telegram water meter filter
# supports keyword filter, forward source filter(chat id based)

@register_hook(src_driver='Telegram')
async def message_hook_func(message: UnifiedMessage) -> bool:
    # filter source
    if message.chat_attrs.forward_from and message.chat_attrs.forward_from.chat_id in config['ChatID']:
        await quick_reply(message.chat_attrs, 'Message blocked by rule (channel)')
        return True

    # filter keyword
    raw_text = assemble_message(message).lower()
    for keyword in config['Keyword']:
        if keyword in raw_text:
            await quick_reply(message.chat_attrs, f'Message blocked by rule (keyword: {keyword})')
            return True

    return False


def save_config():
    yaml.dump(config, open(yaml_config_dir, 'w'))


@register_command(cmd=['block_channel', 'bc'], platform='Telegram', description='register block channel',
                  privilege=Privilege.BOT_ADMIN)
async def command(chat_attrs: ChatAttribute, args: List):
    global config
    if not chat_attrs.reply_to:
        await quick_reply(chat_attrs, 'Message not specified, please reply to a message')
        return False
    reply_chat_attrs = chat_attrs.reply_to
    if not reply_chat_attrs.forward_from:  # definitely not a channel
        await quick_reply(chat_attrs, 'Message is not a forward')
        return False
    if reply_chat_attrs.forward_from.chat_id >= 0:
        await quick_reply(chat_attrs, 'Message is not from channel')
        return False
    channel_id = reply_chat_attrs.forward_from.chat_id
    if channel_id in config['ChatID']:
        await quick_reply(chat_attrs, 'Channel already exists')
    else:
        config['ChatID'].append(reply_chat_attrs.forward_from.chat_id)
        save_config()
        await quick_reply(chat_attrs, f'Success, added channel {reply_chat_attrs.forward_from.name}')


@register_command(cmd=['block_keyword', 'bw'], platform='Telegram', description='register block keyword',
                  privilege=Privilege.BOT_ADMIN)
async def command(chat_attrs: ChatAttribute, args: List):
    global config

    if not args:
        await quick_reply(chat_attrs, 'Empty keyword list')
        return False

    old_keywords = set(config['Keyword'])
    new_keywords = set(args)

    exists_keywords = old_keywords & new_keywords
    added_keywords = new_keywords - exists_keywords
    if added_keywords:
        config['Keyword'] = list(old_keywords | new_keywords)
        save_config()
        if exists_keywords:
            await quick_reply(chat_attrs, f'Success, added keywords: {", ".join(added_keywords)}\n'
                                          f'exists keywords: {", ".join(exists_keywords)}')
        await quick_reply(chat_attrs, f'Success, added keywords: {", ".join(added_keywords)}')
    else:
        await quick_reply(chat_attrs, f'All keyword exists: {", ".join(exists_keywords)}')
