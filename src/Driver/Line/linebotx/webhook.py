import asyncio
import inspect

from linebot.models.events import MessageEvent
from linebot.webhook import WebhookHandler
from linebot.utils import LOGGER


class WebhookHandlerAsync(WebhookHandler):
    def __init__(self, channel_secret):
        super().__init__(channel_secret)

    def add(self, event, message=None):
        def decorator(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("Handler must be a coroutine function")

            if isinstance(message, (list, tuple)):
                for it in message:
                    self.__add_handler(func, event, message=it)
            else:
                self.__add_handler(func, event, message=message)

            return func

        return decorator

    def default(self):
        def decorator(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("Handler must be a coroutine function")

            self._default = func
            return func

        return decorator

    async def handle(self, body, signature):
        payload = self.parser.parse(body, signature, as_payload=True)

        for event in payload.events:
            func = None
            key = None

            if isinstance(event, MessageEvent):
                key = self.__get_handler_key(event.__class__, event.message.__class__)
                func = self._handlers.get(key, None)

            if func is None:
                key = self.__get_handler_key(event.__class__)
                func = self._handlers.get(key, None)

            if func is None:
                func = self._default

            if func is None:
                LOGGER.info("No handler of " + key + " and no default handler")
            else:
                args_count = self.__get_args_count(func)
                if args_count == 0:
                    await func()
                elif args_count == 1:
                    await func(event)
                else:
                    await func(event, payload.destination)

    def __add_handler(self, func, event, message=None):
        key = self.__get_handler_key(event, message=message)
        self._handlers[key] = func

    @staticmethod
    def __get_args_count(func):
        arg_spec = inspect.getfullargspec(func)
        return len(arg_spec.args)

    @staticmethod
    def __get_handler_key(event, message=None):
        if message is None:
            return event.__name__
        else:
            return event.__name__ + "_" + message.__name__
