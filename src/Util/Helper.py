from typing import List, Union, Dict, Callable, Any, Tuple
import logging
from janus import Queue
from Core.UMRType import UnifiedMessage, EntityType, MessageEntity
from Core.UMRLogging import get_logger
from functools import partial

logger = get_logger('Util.Helper')


# test attributes in config.yaml
def check_attribute(config: Dict, attributes: List[Tuple[str, bool, Any]], logger: logging.Logger):
    """
    Test if attributes exist in config
    :param config: config file
    :param attributes: Tuple of [attribute, optional, optional value]
    :param logger: log to this logger
    :return:
    """
    for attr in attributes:
        attribute, optional, optional_value = attr
        if attribute not in config:
            if not optional:
                logger.error(f'{attr} not found in config.yaml')
                exit(-1)
            else:
                config[attribute] = optional_value


# async put new task to janus queue
async def janus_queue_put_async(_janus_queue: Queue, func: Callable, *args, **kwargs):
    await _janus_queue.async_q.put((func, args, kwargs))


# sync put new task to janus queue
def janus_queue_put_sync(_janus_queue: Queue, func: Callable, *args, **kwargs):
    _janus_queue.sync_q.put((func, args, kwargs))


def escape_markdown(text: str):
    """
    return text escaped given entity types
    :param text: text to escape
    :param entity_type: entities to escape
    :return:
    """
    # de-escape and escape again to avoid double escaping
    return text.replace('\\*', '*').replace('\\`', '`').replace('\\_', '_')\
        .replace('\\~', '~').replace('\\>', '>').replace('\\[', '[')\
        .replace('\\]', ']').replace('\\(', '(').replace('\\)', ')')\
        .replace('*', '\\*').replace('`', '\\`').replace('_', '\\_')\
        .replace('~', '\\~').replace('>', '\\>').replace('[', '\\[')\
        .replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')


def escape_html(text: str):
    """
    return escaped text
    :param text: text to escape
    :return:
    """
    return text.replace('<', '&lt;').replace('>', '&gt;')


def unparse_entities(message: UnifiedMessage, support_entities: EntityType, to_type='html'):
    """
    parse plain text with entities to html
    :param message:
    :param support_entities:
    :return: html text
    """
    if to_type == 'html':
        escape_function = escape_html
        entity_start = {
            EntityType.PLAIN:         '',
            EntityType.BOLD:          '<b>',
            EntityType.ITALIC:        '<i>',
            EntityType.CODE:          '<code>',
            EntityType.CODE_BLOCK:    '<pre>',
            EntityType.UNDERLINE:     '<u>',
            EntityType.STRIKETHROUGH: '<s>',
            EntityType.QUOTE:         '',
            EntityType.QUOTE_BLOCK:   '',
            EntityType.LINK:          '<a href={}>',
        }

        entity_end = {
            EntityType.PLAIN:         '',
            EntityType.BOLD:          '</b>',
            EntityType.ITALIC:        '</i>',
            EntityType.CODE:          '</code>',
            EntityType.CODE_BLOCK:    '</pre>',
            EntityType.UNDERLINE:     '</u>',
            EntityType.STRIKETHROUGH: '</s>',
            EntityType.QUOTE:         '',
            EntityType.QUOTE_BLOCK:   '',
            EntityType.LINK:          '</a>',
        }
    else:
        entity_start = {
            EntityType.PLAIN:         '',
            EntityType.BOLD:          '**',
            EntityType.ITALIC:        '*',
            EntityType.CODE:          '`',
            EntityType.CODE_BLOCK:    '```',
            EntityType.UNDERLINE:     '__',
            EntityType.STRIKETHROUGH: '~~',
            EntityType.QUOTE:         '> ',
            EntityType.QUOTE_BLOCK:   '>>> ',
            EntityType.LINK:          '[Link]({}) ',
        }

        entity_end = {
            EntityType.PLAIN:         '',
            EntityType.BOLD:          '**',
            EntityType.ITALIC:        '*',
            EntityType.CODE:          '`',
            EntityType.CODE_BLOCK:    '```',
            EntityType.UNDERLINE:     '__',
            EntityType.STRIKETHROUGH: '~~',
            EntityType.QUOTE:         '',
            EntityType.QUOTE_BLOCK:   '',
            EntityType.LINK:          '',
        }
        escape_function = escape_markdown
    
    if not message.message_entities:
        return escape_function(message.message)

    stack: List[MessageEntity] = list()
    result = ''
    offset = 0
    for entity in message.message_entities:
        while stack and entity.start > stack[-1].end:
            _entity = stack[-1]
            if offset < _entity.end:
                result += escape_function(message.message[offset:_entity.end])
            if support_entities & _entity.entity_type:
                result += entity_end[_entity.entity_type]
            offset = _entity.end
            stack.pop()

        if entity.start > offset:
            result += escape_function(message.message[offset:entity.start])
            offset = entity.start
        
        if entity.entity_type == EntityType.LINK:
            if support_entities & entity.entity_type: 
                result += entity_start[entity.entity_type].format(entity.link)
            else:
                result += f'link: {entity.link} title: '
        else:
            if support_entities & entity.entity_type:
                result += entity_start[entity.entity_type]
        stack.append(entity)

    while stack:
        _entity = stack[-1]
        if offset < _entity.end:
            result += escape_function(message.message[offset:_entity.end])
        if support_entities & _entity.entity_type:
            result += entity_end[_entity.entity_type]
        offset = _entity.end
        stack.pop()

    if offset < len(message.message):
        result += escape_function(message.message[offset:])

    return result


def unparse_entities_to_html(message: UnifiedMessage, support_entities: EntityType):
    """
    parse plain text with entities to html
    :param message:
    :param support_entities:
    :return:
    """
    return unparse_entities(message, support_entities, to_type='html')


def unparse_entities_to_markdown(message: UnifiedMessage, support_entities: EntityType):
    """
    parse plain text with entities to markdown
    :param message:
    :param support_entities:
    :return:
    """
    return unparse_entities(message, support_entities, to_type='markdown')
