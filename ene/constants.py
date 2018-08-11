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

"""This module conatins common constants."""
import sys
from pathlib import Path

IS_37 = sys.version_info >= (3, 7)

if IS_37:
    # noinspection PyUnresolvedReferences
    from importlib import resources # pylint: disable=E0611,W0611
else:
    # noinspection PyUnresolvedReferences
    import importlib_resources as resources # pylint: disable=E0611,W0611

IS_WIN = sys.platform in ('win32', 'cygwin')
IS_LINUX = sys.platform.startswith('linux')
IS_MAC = sys.platform == 'darwin'

APP_NAME = 'ENE'
CLIENT_ID = 584

CONFIG_DIR = Path.home() / '.config' / 'ene'
GRAPHQL_URL = 'https://graphql.anilist.co'

CONFIG_ITEM = {
    'player_type': 'Player',
    'player_path': 'Player Path',
    'use_rc': 'VLC RC Interface'
}
