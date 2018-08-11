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
from functools import lru_cache


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
    """Opens source code of ene in a webbrowser."""
    webbrowser.open('https://github.com/MaT1g3R/ene/')
