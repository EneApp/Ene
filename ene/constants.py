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

import sys
from functools import lru_cache

IS_WIN = sys.platform in ('win32', 'cygwin')
IS_LINUX = sys.platform.startswith('linux')
IS_MAC = sys.platform == 'darwin'
IS_37 = sys.version_info >= (3, 7)


@lru_cache(None)
def load_file(path):
    """
    Read file content and put it in cache

    Args:
        path: Path to the file

    Returns:
        The file content
    """
    with open(path) as f:
        return f.read()
