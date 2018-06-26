#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018 Peijun Ma, Justin Sedge
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from functools import lru_cache, partial, wraps
from time import time
from typing import Optional, Callable


@lru_cache(None)
def strip_html(s: str) -> str:
    """
    Strip html tags from a string
    Args:
        s: The string

    Returns:
        The string with html tags stripped
    """
    return re.sub('<[^<]+?>', '', s)


def cache(func=None, *, timeout: Optional[int] = 300) -> Callable:
    """
    Decorator to cache a method.

    Class must have a ``_cache`` and a ``_timeout`` attribute
    Args:
        func: Function decorated
        timeout: Timeout in seconds for the result to expire

    Returns:
        Wrapped method
    """
    if not func:
        return partial(cache, timeout=timeout)

    @wraps(cache)
    def wrapper(self, *args, **kwargs):
        name = func.__name__
        key = (name, args, ((k, v) for k, v in kwargs.items())) if kwargs else (name, args)
        last_time = self._timeout.get(key)

        if key in self._cache and \
                (not timeout or
                 (timeout and last_time and time() - last_time < timeout)):
            return self._cache[key]

        res = func(self, *args, **kwargs)
        self._cache[key] = res
        if timeout:
            self._timeout[key] = time()
        return res

    return wrapper


def cached_property(func=None, *, timeout: Optional[int] = 300):
    """
    Decorator to cache a property.

    Class must have a ``_cache`` and a ``_timeout`` attribute
    Args:
        func: Function decorated
        timeout: Timeout in seconds for the result to expire

    Returns:
        Wrapped property
    """
    if not func:
        return partial(cached_property, timeout=timeout)
    return property(cache(func=func, timeout=timeout))
