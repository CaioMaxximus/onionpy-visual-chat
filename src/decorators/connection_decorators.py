import functools
from typing import Any, Callable
from src.error.special_errors import ConnetionClosedError


def validate_connection_state(func : Callable) -> Callable:

    @functools.wraps(func)
    async def inner_wrapper(self ,*args, **kwargs):
        if self._connected:
            return await func(self,*args, **kwargs)
        else:
            raise ConnetionClosedError("The connection didnt start yet!")
    return inner_wrapper