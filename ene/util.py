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

"""This module contains various helper function"""
import re
import webbrowser
from functools import lru_cache, singledispatch, update_wrapper
from pathlib import Path
from typing import Callable, Optional

from requests import get


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


def open_source_code():
    """Opens source code of ene in a web browser."""
    webbrowser.open('https://github.com/MaT1g3R/ene/')


def get_resource(url: str, cache_home: Path) -> Path:
    """
    Download and return a path for a resource from url.

    Args:
        url: The resource url
        cache_home: Cache directory path

    Returns:
        Downloaded resource path
    """
    path = Path(cache_home, url.partition('anilist.co/')[-1])
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        res = get(url)
        path.write_bytes(res.content)
    return path


def dict_filter(dict_: dict, filter_: Optional[Callable] = None) -> dict:
    """
    Filter a dictionary by a given filter function

    Args:
        dict_: The dict to filter
        filter_:
            The filter function, takes the dict key and values as arguments,
            defaults to checking for both the key and value to be not None

    Returns:
        The filtered dict
    """
    filter_func = filter_ if filter_ else lambda key, val: key is not None and val is not None
    return {key: val for key, val in dict_.items() if filter_func(key, val)}


def method_dispatch(func):
    """
    Decorator to use functools.singledispatch on methods

    Args:
        func: The method to dispatch

    Returns:
        The single dispatched method
    """
    dispatcher = singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper
