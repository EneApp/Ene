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

from time import sleep, time

import pytest

from ene.util import cache


class Dummy:
    def __init__(self):
        self._timeout = {}
        self._cache = {}

    @property
    @cache(timeout=1)
    def foo(self):
        return 'foo'

    @cache
    def bar(self):
        return 'bar'


class TestCache:

    @pytest.fixture
    def d(self):
        return Dummy()

    def test_cache_hit(self, d):
        d._cache[('bar', ())] = 'baz'
        assert d.bar() == 'baz'

    def test_cache_hit_time(self, d):
        f = d.foo
        del f
        sleep(0.5)
        d._cache[('foo', ())] = 'bar'
        assert d.foo == 'bar'

    def test_cache_miss(self, d):
        d._cache['foo'] = 'o'
        assert d.bar() == 'bar'
        assert d._cache[('bar', ())] == 'bar'

    def test_cache_miss_not_timedout(self, d):
        d._cache['bar'] = 'asdasd'
        assert d.foo == 'foo'
        assert d._cache[('foo', ())] == 'foo'
        assert time() - d._timeout[('foo', ())] < 1

    def test_cache_miss_timeout(self, d):
        d._cache[('foo', ())] = 'asd'
        d._timeout[('foo', ())] = time() - 10

        assert d.foo == 'foo'
        assert d._cache[('foo', ())] == 'foo'
        assert time() - d._timeout[('foo', ())] < 1
