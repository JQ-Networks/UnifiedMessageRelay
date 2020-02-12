"""
此模块提供了 CQHTTP API 的接口类。
"""

import abc
import functools
from typing import Callable, Any, Union, Awaitable


class Api:
    """
    API 接口类。

    继承此类的具体实现类应实现 `call_action` 方法。
    """

    @abc.abstractmethod
    def call_action(self, action: str, **params) -> Union[Awaitable[Any], Any]:
        """
        调用 CQHTTP API，`action` 为要调用的 API 动作名，`**params`
        为 API 所需参数。

        根据实现类的不同，此函数可能是异步也可能是同步函数。
        """
        pass

    def __getattr__(self,
                    item: str) -> Callable[..., Union[Awaitable[Any], Any]]:
        """获取一个可调用对象，用于调用对应 API。"""
        return functools.partial(self.call_action, item)
