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

"""This module contains common constants."""
import sys
from os import getenv
from pathlib import Path

from result import Err

IS_37 = sys.version_info >= (3, 7)

IS_WIN = sys.platform in ('win32', 'cygwin')
IS_LINUX = sys.platform.startswith('linux')
IS_MAC = sys.platform == 'darwin'

_DATA_HOME = getenv('XDG_DATA_HOME')
_CONFIG_HOME = getenv('XDG_CONFIG_HOME')
_CACHE_HOME = getenv('XDG_CACHE_HOME')
_HOME = Path.home()

if _DATA_HOME:
    DATA_HOME = Path(_DATA_HOME, 'ene')
elif IS_WIN:
    DATA_HOME = Path(getenv('APPDATA'), 'ene', 'data')
elif IS_MAC:
    DATA_HOME = _HOME / 'Library' / 'Application Support' / 'ene' / 'data'
else:
    DATA_HOME = _HOME / '.local' / 'share' / 'ene'

if _CONFIG_HOME:
    CONFIG_HOME = Path(_CONFIG_HOME, 'ene')
elif IS_WIN:
    CONFIG_HOME = Path(getenv('APPDATA'), 'ene', 'config')
elif IS_MAC:
    CONFIG_HOME = _HOME / 'Library' / 'Application Support' / 'ene' / 'config'
else:
    CONFIG_HOME = _HOME / '.config' / 'ene'

if _CACHE_HOME:
    CACHE_HOME = Path(_CACHE_HOME, 'ene')
elif IS_WIN:
    CACHE_HOME = Path(getenv('TEMP'), 'ene')
elif IS_MAC:
    CACHE_HOME = _HOME / 'Library' / 'Cache' / 'ene'
else:
    CACHE_HOME = _HOME / '.cache' / 'ene'

APP_NAME = 'ENE'
CLIENT_ID = 584

GRAPHQL_URL = 'https://graphql.anilist.co'

STREAMERS = ('Crunchyroll', 'Funimation', 'Netflix', 'Amazaon', 'Hidive', 'Hulu', 'Animelab')

ERR_NONE = Err(None)
