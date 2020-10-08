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

import pytest

from ene.util import dict_filter


def test_dict_filter_none():
    dict_ = {
        'foo': None,
        None: 'bar',
        '': [],
        (): {}
    }
    assert dict_filter(dict_) == {'': [], (): {}}


def test_dict_filter():
    def filter_(key, val):
        return key == val

    dict_ = {
        'foo': 'foo',
        'bar': 'baz',
        (): ()
    }

    assert dict_filter(dict_, filter_) == {'foo': 'foo', (): ()}


def test_dict_filter_too_few_args():
    def filter_(arg):
        return True

    with pytest.raises(TypeError):
        dict_filter({'': ''}, filter_)


def test_dict_filter_too_many_args():
    def filter_(arg, argg, arggg):
        return True

    with pytest.raises(TypeError):
        dict_filter({'': ''}, filter_)
