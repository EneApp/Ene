#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2020 Peijun Ma, Justin Sedge
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
from os import getenv
from pathlib import Path
from shutil import rmtree

import pytest

HERE = Path(__file__).parent.resolve()
CONFIG_HOME = HERE / '.config'
DATA_HOME = HERE / '.data'
CACHE_HOME = HERE / '.cache'

skip_travis_osx = pytest.mark.skipif(
    getenv('TRAVIS_OS_NAME') == 'osx',
    reason='does not run on travis macOS'
)


def rmdir(path, force):
    try:
        rmtree(path)
    except FileNotFoundError:
        if force:
            pass
        else:
            raise
