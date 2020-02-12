"""
此模块提供了默认 bot 对象及用于控制和使用它的相关函数、对象、和装饰器。
"""

from . import CQHttp
from .api_impl import LazyApi

__all__ = [
    'default_bot', 'default_server_app', 'api', 'sync_api',
    'reconfigure_default_bot', 'run', 'send',
    'on', 'on_message', 'on_notice', 'on_request', 'on_meta_event',
]

__pdoc__ = {}

default_bot = CQHttp()
"""默认 bot 对象。"""

default_server_app = default_bot.server_app
"""默认 bot 对象的 Quart app。"""

api = default_bot.api
"""默认 bot 对象的 `aiocqhttp.api_impl.AsyncApi` 对象，用于异步地调用 CQHTTP API。"""

sync_api = LazyApi(lambda: default_bot.sync)
"""默认 bot 对象的 `aiocqhttp.api_impl.SyncApi` 对象，用于同步地调用 CQHTTP API。"""

reconfigure_default_bot = default_bot._configure
__pdoc__['reconfigure_default_bot'] = """
重新配置默认 bot 对象。
"""

run = default_bot.run
__pdoc__['run'] = """
运行默认 bot 对象。
"""

send = default_bot.send
__pdoc__['send'] = """
使用默认 bot 对象发送消息。
"""

on = default_bot.on
__pdoc__['on'] = """
注册默认 bot 对象的事件处理函数，用作装饰器。
"""

on_message = default_bot.on_message
__pdoc__['on_message'] = """
注册默认 bot 对象的消息事件处理函数，用作装饰器。
"""

on_notice = default_bot.on_notice
__pdoc__['on_notice'] = """
注册默认 bot 对象的通知事件处理函数，用作装饰器。
"""

on_request = default_bot.on_request
__pdoc__['on_request'] = """
注册默认 bot 对象的请求事件处理函数，用作装饰器。
"""

on_meta_event = default_bot.on_meta_event
__pdoc__['on_meta_event'] = """
注册默认 bot 对象的元事件处理函数，用作装饰器。
"""
