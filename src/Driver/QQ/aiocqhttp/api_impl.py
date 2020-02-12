"""
此模块提供了 CQHTTP API 相关的实现类。
"""

import abc
import asyncio
import sys
from typing import Callable, Dict, Any, Optional, Union, Awaitable

from .api import Api

try:
    import ujson as json
except ImportError:
    import json

import httpx
from Lib.quart import websocket as event_ws
from Lib.quart.wrappers.request import Websocket

from .exceptions import ActionFailed, ApiNotAvailable, HttpFailed, NetworkError
from .utils import sync_wait

__pdoc__ = {
    'ResultStore': False,
}


class AsyncApi(Api):
    """
    异步 API 接口类。

    继承此类的具体实现类应实现异步的 `call_action` 方法。
    """

    @abc.abstractmethod
    async def call_action(self, action: str, **params) -> Any:
        pass


def _handle_api_result(result: Optional[Dict[str, Any]]) -> Any:
    """
    Retrieve 'data' field from the API result object.

    :param result: API result that received from CQHTTP
    :return: the 'data' field in result object
    :raise ActionFailed: the 'status' field is 'failed'
    """
    if isinstance(result, dict):
        if result.get('status') == 'failed':
            raise ActionFailed(retcode=result.get('retcode'))
        return result.get('data')


class HttpApi(AsyncApi):
    """
    HTTP API 实现类。

    实现通过 HTTP 调用 CQHTTP API。
    """

    def __init__(self, api_root: Optional[str], access_token: Optional[str]):
        super().__init__()
        self._api_root = api_root.rstrip('/') if api_root else None
        self._access_token = access_token

    async def call_action(self, action: str, **params) -> Any:
        if not self._is_available():
            raise ApiNotAvailable

        headers = {}
        if self._access_token:
            headers['Authorization'] = 'Bearer ' + self._access_token

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self._api_root + '/' + action,
                                         json=params, headers=headers)
            if 200 <= resp.status_code < 300:
                return _handle_api_result(json.loads(resp.text))
            raise HttpFailed(resp.status_code)
        except httpx.InvalidURL:
            raise NetworkError('API root url invalid')
        except httpx.HTTPError:
            raise NetworkError('HTTP request failed')

    def _is_available(self) -> bool:
        return bool(self._api_root)


class _SequenceGenerator:
    _seq = 1

    @classmethod
    def next(cls) -> int:
        s = cls._seq
        cls._seq = (cls._seq + 1) % sys.maxsize
        return s


class ResultStore:
    _futures: Dict[int, asyncio.Future] = {}

    @classmethod
    def add(cls, result: Dict[str, Any]):
        if isinstance(result.get('echo'), dict) and \
                isinstance(result['echo'].get('seq'), int):
            future = cls._futures.get(result['echo']['seq'])
            if future:
                future.set_result(result)

    @classmethod
    async def fetch(cls, seq: int) -> Dict[str, Any]:
        future = asyncio.get_event_loop().create_future()
        cls._futures[seq] = future
        try:
            return await asyncio.wait_for(future, 60)  # wait for only 60 secs
        except asyncio.TimeoutError:
            # haven't received any result until timeout,
            # we consider this API call failed with a network error.
            raise NetworkError('WebSocket API call timeout')
        finally:
            # don't forget to remove the future object
            del cls._futures[seq]


class WebSocketReverseApi(AsyncApi):
    """
    反向 WebSocket API 实现类。

    实现通过反向 WebSocket 调用 CQHTTP API。
    """

    def __init__(self, connected_clients: Dict[str, Websocket]):
        super().__init__()
        self._clients = connected_clients

    async def call_action(self, action: str, **params) -> Any:
        api_ws = None
        if self._is_available():
            api_ws = self._clients.get(event_ws.headers['X-Self-ID'])
        elif params.get('self_id'):
            api_ws = self._clients.get(str(params['self_id']))
        elif len(self._clients) == 1:
            api_ws = list(self._clients.values())[0]

        if not api_ws:
            raise ApiNotAvailable

        seq = _SequenceGenerator.next()
        await api_ws.send(json.dumps({
            'action': action, 'params': params, 'echo': {'seq': seq}
        }))
        return _handle_api_result(await ResultStore.fetch(seq))

    def _is_available(self) -> bool:
        # available only when current event ws has a corresponding api ws
        return event_ws and event_ws.headers['X-Self-ID'] in self._clients


class UnifiedApi(AsyncApi):
    """
    统一 API 实现类。

    同时维护 `HttpApi` 和 `WebSocketReverseApi` 对象，根据可用情况，选择两者中的某个使用。
    """

    def __init__(self,
                 http_api: Optional[AsyncApi] = None,
                 wsr_api: Optional[AsyncApi] = None):
        super().__init__()
        self._http_api = http_api
        self._wsr_api = wsr_api

    async def call_action(self, action: str, **params) -> Any:
        result = None
        succeeded = False

        if self._wsr_api:
            # WebSocket is preferred
            try:
                result = await self._wsr_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded and self._http_api:
            try:
                result = await self._http_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded:
            raise ApiNotAvailable
        return result


class SyncApi(Api):
    """
    封装 `AsyncApi` 对象，使其可同步地调用。
    """

    def __init__(self, async_api: AsyncApi, loop: asyncio.AbstractEventLoop):
        """
        `async_api` 参数为 `AsyncApi` 对象，`loop` 参数为用来执行 API
        调用的 event loop。
        """
        self._async_api = async_api
        self._loop = loop

    def call_action(self, action: str, **params) -> Any:
        """同步地调用 CQHTTP API。"""
        return sync_wait(
            coro=self._async_api.call_action(action, **params),
            loop=self._loop
        )


class LazyApi(Api):
    """
    延迟获取 `aiocqhttp.api.Api` 对象。
    """

    def __init__(self, api_getter: Callable[[], Union[Api]]):
        self._api_getter = api_getter

    def call_action(self, action: str, **params) -> Union[Awaitable[Any], Any]:
        """获取 `Api` 对象，并调用 CQHTTP API。"""
        api = self._api_getter()
        return api.call_action(action, **params)
