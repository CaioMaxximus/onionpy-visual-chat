import functools
from typing import Any, Callable
from src.error.special_errors import ConnectionClosedError


def validate_connection_state(func : Callable) -> Callable:

    @functools.wraps(func)
    async def inner_wrapper(self ,*args, **kwargs):
        if self._connected:
            return await func(self,*args, **kwargs)
        else:
            raise ConnectionClosedError("The connection didnt start yet!")
    return inner_wrapper