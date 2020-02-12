"""
此模块提供事件总线相关类。
"""

import asyncio
from collections import defaultdict
from typing import Callable, List, Any


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(set)

    def subscribe(self, event: str, func: Callable) -> None:
        self._subscribers[event].add(func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        if func in self._subscribers[event]:
            self._subscribers[event].remove(func)

    def on(self, event: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.subscribe(event, func)
            return func

        return decorator

    async def emit(self, event: str, *args, **kwargs) -> List[Any]:
        results = []
        while True:
            coros = []
            for f in self._subscribers[event]:
                coros.append(f(*args, **kwargs))
            if coros:
                results += await asyncio.gather(*coros)
            event, *sub_event = event.rsplit('.', maxsplit=1)
            if not sub_event:
                # the current event is the root event
                break
        return results
