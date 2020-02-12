import asyncio

import httpx

from linebot.http_client import HttpClient, HttpResponse
import json


class HttpXClient(HttpClient):
    """HttpClient implemented by httpx."""

    DEFAULT_TIMEOUT = 30

    def __init__(self, timeout=DEFAULT_TIMEOUT):
        self.session = httpx.AsyncClient(timeout=timeout)
        self.timeout = timeout

    async def get(self, url, headers=None, params=None, stream=False, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = await self.session.get(url, headers=headers, params=params, timeout=timeout)
        return AioHttpResponse(response)

    async def post(self, url, headers=None, data=None, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = await self.session.post(url, headers=headers, data=data, timeout=timeout)
        return AioHttpResponse(response)

    async def delete(self, url, headers=None, params=None, timeout=None):
        if timeout is None:
            timeout = self.timeout

        response = await self.session.delete(
            url, headers=headers, params=params, timeout=timeout
        )

        return AioHttpResponse(response)

    async def close(self):
        await self.session.aclose()


class AioHttpResponse(HttpResponse):
    """HttpResponse implemented by aiohttp lib's response."""

    def __init__(self, response: httpx.Response):
        self.response = response

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    async def text(self):
        return self.response.text

    @property
    async def content(self):
        return self.response.content

    @property
    async def json(self):
        return self.response.json()

    def iter_content(self, chunk_size=1024, decode_unicode=False):
        return self.response.iter_bytes()
