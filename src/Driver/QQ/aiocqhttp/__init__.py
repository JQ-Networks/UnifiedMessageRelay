"""
此模块主要提供了 `CQHttp` 类（类似于 Flask 的 `Flask` 类和 Quart 的 `Quart`
类）；除此之外，还从 `message`、`event`、`exceptions`
模块导入了一些常用的类、模块变量和函数，以便于使用。
"""

import asyncio
import hmac
import logging
import re
from typing import (Dict, Any, Optional, AnyStr, Callable, Union, List,
                    Awaitable)

try:
    import ujson as json
except ImportError:
    import json

from Lib.quart import Quart, request, abort, jsonify, websocket, Response

from .api_impl import (AsyncApi, SyncApi, HttpApi, WebSocketReverseApi,
                       UnifiedApi, ResultStore)
from .bus import EventBus
from .exceptions import Error, TimingError
from .event import Event
from .message import Message, MessageSegment
from .utils import ensure_async

from . import exceptions
from .exceptions import *  # noqa: F401, F403

__all__ = [
    'CQHttp', 'Event', 'Message', 'MessageSegment',
]
__all__ += exceptions.__all__

__pdoc__ = {}


def _deco_maker(type_: str) -> Callable:
    def deco_deco(self, arg: Optional[Union[str, Callable]] = None,
                  *sub_event_names: str) -> Callable:
        def deco(func: Callable) -> Callable:
            if isinstance(arg, str):
                e = [type_ + '.' + e for e in [arg] + list(sub_event_names)]
                self.on(*e)(func)
            else:
                self.on(type_)(func)
            return func

        if isinstance(arg, Callable):
            return deco(arg)
        return deco

    return deco_deco


class CQHttp(AsyncApi):
    """
    CQHTTP 机器人的主类，负责控制整个机器人的运行、事件处理函数的注册、与 CQHTTP
    的连接、CQHTTP API 的调用等。

    内部维护了一个 `Quart` 对象作为 web 服务器，提供 HTTP 协议的 ``/`` 和 WebSocket
    协议的 ``/ws/``、``/ws/api/``、``/ws/event/`` 端点供 CQHTTP 连接。

    由于基类 `api_impl.AsyncApi` 继承了 `api.Api` 的 `__getattr__`
    魔术方法，因此可以在 bot 对象上直接调用 CQHTTP API，例如：

    ```py
    await bot.send_private_msg(user_id=10001000, message='你好')
    friends = await bot.get_friend_list()
    ```

    也可以通过 `CQHttp.call_action` 方法调用 API，例如：

    ```py
    await bot.call_action('set_group_whole_ban', group_id=10010)
    ```

    两种调用 API 的方法最终都通过 `CQHttp.api` 属性来向 CQHTTP
    发送请求并获取调用结果。
    """

    def __init__(self, *,
                 api_root: Optional[str] = None,
                 access_token: Optional[str] = None,
                 secret: Optional[AnyStr] = None,
                 message_class: Optional[type] = None,
                 **kwargs):
        """
        ``api_root`` 参数为 CQHTTP API 的 URL，``access_token`` 和
        ``secret`` 参数为 CQHTTP 配置中填写的对应项。

        ``message_class`` 参数为要用来对 `Event.message` 进行转换的消息类，可使用
        `Message`，例如：

        ```py
        from aiocqhttp import CQHttp, Message

        bot = CQHttp(message_class=Message)

        @bot.on_message
        async def handler(event):
            # 这里 event.message 已经被转换为 Message 对象
            assert isinstance(event.message, Message)
        ```
        """
        self._api = UnifiedApi()
        self._sync_api = None
        self._bus = EventBus()
        self._loop = None

        self._server_app = Quart(__name__)
        self._server_app.before_serving(self._before_serving)
        self._server_app.add_url_rule('/', methods=['POST'],
                                      view_func=self._handle_http_event)
        for p in ('/ws', '/ws/event', '/ws/api'):
            self._server_app.add_websocket(p, strict_slashes=False,
                                           view_func=self._handle_wsr)

        self._configure(api_root, access_token, secret, message_class)

    def _configure(self,
                   api_root: Optional[str] = None,
                   access_token: Optional[str] = None,
                   secret: Optional[AnyStr] = None,
                   message_class: Optional[type] = None):
        self._message_class = message_class
        self._access_token = access_token
        self._secret = secret
        self._api._http_api = HttpApi(api_root, access_token)
        self._wsr_api_clients = {}  # connected wsr api clients
        self._api._wsr_api = WebSocketReverseApi(self._wsr_api_clients)

    async def _before_serving(self):
        self._loop = asyncio.get_running_loop()

    @property
    def asgi(self) -> Callable[[dict, Callable, Callable], Awaitable]:
        """ASGI app 对象，可使用支持 ASGI 的 web 服务器软件部署。"""
        return self._server_app

    @property
    def server_app(self) -> Quart:
        """Quart app 对象，可用来对 Quart 的运行做精细控制，或添加新的路由等。"""
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        """Quart app 的 logger，等价于 ``bot.server_app.logger``。"""
        return self._server_app.logger

    @property
    def loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """Quart app 所在的 event loop，在 app 运行之前为 `None`。"""
        return self._loop

    @property
    def api(self) -> AsyncApi:
        """`api_impl.AsyncApi` 对象，用于异步地调用 CQHTTP API。"""
        return self._api

    @property
    def sync(self) -> SyncApi:
        """
        `api_impl.SyncApi` 对象，用于同步地调用 CQHTTP API，例如：

        ```py
        @bot.on_message('group')
        def sync_handler(event):
            user_info = bot.sync.get_group_member_info(
                group_id=event.group_id, user_id=event.user_id
            )
            ...
        ```
        """
        if not self._sync_api:
            if not self._loop:
                raise TimingError('attempt to access sync api '
                                  'before bot is running')
            self._sync_api = SyncApi(self._api, self._loop)
        return self._sync_api

    def run(self, host: str = None, port: int = None, *args, **kwargs) -> None:
        """运行 bot 对象，实际就是运行 Quart app，参数与 `Quart.run` 一致。"""
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def call_action(self, action: str, **params) -> Any:
        """
        通过内部维护的 `api_impl.AsyncApi` 具体实现类调用 CQHTTP API，``action``
        为要调用的 API 动作名，``**params`` 为 API 所需参数。
        """
        return await self._api.call_action(action=action, **params)

    async def send(self, event: Event,
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs) -> Optional[Dict[str, Any]]:
        """
        向触发事件的主体发送消息。

        ``event`` 参数为事件对象，``message`` 参数为要发送的消息。可额外传入 ``at_sender``
        命名参数用于控制是否 at 事件的触发者，默认为 `False`。其它命名参数作为
        CQHTTP API ``send_msg`` 的参数直接传递。
        """
        at_sender = kwargs.pop('at_sender', False) and 'user_id' in event

        params = event.copy()
        params['message'] = message
        params.pop('raw_message', None)  # avoid wasting bandwidth
        params.pop('comment', None)
        params.pop('sender', None)
        params.update(kwargs)

        if 'message_type' not in params:
            if 'group_id' in params:
                params['message_type'] = 'group'
            elif 'discuss_id' in params:
                params['message_type'] = 'discuss'
            elif 'user_id' in params:
                params['message_type'] = 'private'

        if at_sender and params['message_type'] != 'private':
            params['message'] = MessageSegment.at(params['user_id']) + \
                                MessageSegment.text(' ') + params['message']

        return await self.send_msg(**params)

    def subscribe(self, event_name: str, func: Callable) -> None:
        """注册事件处理函数。"""
        self._bus.subscribe(event_name, ensure_async(func))

    def unsubscribe(self, event_name: str, func: Callable) -> None:
        """取消注册事件处理函数。"""
        self._bus.unsubscribe(event_name, func)

    def on(self, *event_names: str) -> Callable:
        """
        注册事件处理函数，用作装饰器，例如：

        ```py
        @bot.on('notice.group_decrease', 'notice.group_increase')
        async def handler(event):
            pass
        ```

        参数为要注册的事件名，格式是点号分割的各级事件类型，见 `Event.name`。

        可以多次调用，一个函数可作为多个事件的处理函数，一个事件也可以有多个处理函数。

        可以按不同粒度注册处理函数，例如：

        ```py
        @bot.on('message')
        async def handle_message(event):
            pass

        @bot.on('message.private')
        async def handle_private_message(event):
            pass

        @bot.on('message.private.friend')
        async def handle_friend_private_message(event):
            pass
        ```

        当收到好友私聊消息时，会首先运行 ``handle_friend_private_message``，然后运行
        ``handle_private_message``，最后运行 ``handle_message``。
        """

        def deco(func: Callable) -> Callable:
            for name in event_names:
                self.subscribe(name, func)
            return func

        return deco

    on_message = _deco_maker('message')
    __pdoc__['CQHttp.on_message'] = """
    注册消息事件处理函数，用作装饰器，例如：

    ```
    @bot.on_message('private')
    async def handler(event):
        pass
    ```

    这等价于：

    ```
    @bot.on('message.private')
    async def handler(event):
        pass
    ```

    也可以不加参数，表示注册为所有消息事件的处理函数，例如：

    ```
    @bot.on_message
    async def handler(event):
        pass
    ```
    """

    on_notice = _deco_maker('notice')
    __pdoc__['CQHttp.on_notice'] = "注册通知事件处理函数，用作装饰器，用法同上。"

    on_request = _deco_maker('request')
    __pdoc__['CQHttp.on_request'] = "注册请求事件处理函数，用作装饰器，用法同上。"

    on_meta_event = _deco_maker('meta_event')
    __pdoc__['CQHttp.on_meta_event'] = "注册元事件处理函数，用作装饰器，用法同上。"

    async def _handle_http_event(self) -> Response:
        if self._secret:
            if 'X-Signature' not in request.headers:
                self.logger.warning('signature header is missed')
                abort(401)

            sec = self._secret
            sec = sec.encode('utf-8') if isinstance(sec, str) else sec
            sig = hmac.new(sec, await request.get_data(), 'sha1').hexdigest()
            if request.headers['X-Signature'] != 'sha1=' + sig:
                self.logger.warning('signature header is invalid')
                abort(403)

        payload = await request.json
        if not isinstance(payload, dict):
            abort(400)

        if request.headers['X-Self-ID'] in self._wsr_api_clients:
            self.logger.warning(
                'there is already a reverse websocket api connection, '
                'so the event may be handled twice.')

        response = await self._handle_event(payload)
        if isinstance(response, dict):
            return jsonify(response)
        return Response('', 204)

    async def _handle_wsr(self) -> None:
        if self._access_token:
            auth = websocket.headers.get('Authorization', '')
            m = re.fullmatch(r'(?:[Tt]oken|[Bb]earer) (?P<token>\S+)', auth)
            if not m:
                self.logger.warning('authorization header is missed')
                abort(401)

            token_given = m.group('token').strip()
            if token_given != self._access_token:
                self.logger.warning('authorization header is invalid')
                abort(403)

        role = websocket.headers['X-Client-Role'].lower()
        if role == 'event':
            await self._handle_wsr_event()
        elif role == 'api':
            await self._handle_wsr_api()
        elif role == 'universal':
            await self._handle_wsr_universal()

    async def _handle_wsr_event(self) -> None:
        try:
            while True:
                try:
                    payload = json.loads(await websocket.receive())
                except ValueError:
                    payload = None

                if not isinstance(payload, dict):
                    # ignore invalid payload
                    continue

                asyncio.create_task(self._handle_event_with_response(payload))
        finally:
            pass

    async def _handle_wsr_api(self) -> None:
        self._add_wsr_api_client()
        try:
            while True:
                try:
                    ResultStore.add(json.loads(await websocket.receive()))
                except ValueError:
                    pass
        finally:
            self._remove_wsr_api_client()

    async def _handle_wsr_universal(self) -> None:
        self._add_wsr_api_client()
        try:
            while True:
                try:
                    payload = json.loads(await websocket.receive())
                except ValueError:
                    payload = None

                if not isinstance(payload, dict):
                    # ignore invalid payload
                    continue

                if 'post_type' in payload:
                    # is a event
                    asyncio.create_task(
                        self._handle_event_with_response(payload))
                elif payload:
                    # is a api result
                    ResultStore.add(payload)
        finally:
            self._remove_wsr_api_client()

    def _add_wsr_api_client(self) -> None:
        ws = websocket._get_current_object()
        self_id = websocket.headers['X-Self-ID']
        self._wsr_api_clients[self_id] = ws

    def _remove_wsr_api_client(self) -> None:
        self_id = websocket.headers['X-Self-ID']
        if self_id in self._wsr_api_clients:
            # we must check the existence here,
            # because we allow wildcard ws connections,
            # that is, the self_id may be '*'
            del self._wsr_api_clients[self_id]

    async def _handle_event(self, payload: Dict[str, Any]) -> Any:
        ev = Event.from_payload(payload)
        if not ev:
            return

        event_name = ev.name
        self.logger.info(f'received event: {event_name}')

        if self._message_class and 'message' in ev:
            ev['message'] = self._message_class(ev['message'])
        results = list(filter(lambda r: r is not None,
                              await self._bus.emit(event_name, ev)))
        # return the first non-none result
        return results[0] if results else None

    async def _handle_event_with_response(
            self, payload: Dict[str, Any]) -> None:
        response = await self._handle_event(payload)
        if isinstance(response, dict):
            payload.pop('message', None)  # avoid wasting bandwidth
            payload.pop('raw_message', None)
            payload.pop('comment', None)
            payload.pop('sender', None)
            try:
                await self._api.call_action(
                    self_id=payload['self_id'],
                    action='.handle_quick_operation_async',
                    context=payload, operation=response
                )
            except Error:
                pass
