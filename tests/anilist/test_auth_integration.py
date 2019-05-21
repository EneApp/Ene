#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2019 Peijun Ma, Justin Sedge
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

import webbrowser
from secrets import token_urlsafe

import pytest
from requests import post

from anilist.auth import OAuth
from ene.errors import AuthError
from tests import DATA_HOME, rmdir

CLIENT_ID = 0
TEST_ADDR = '127.0.0.1'


class TestAuth:
    token = token_urlsafe()

    def _setup(self, frag):
        rmdir(DATA_HOME, True)
        redir_url = f'http://127.0.0.1:50000'
        webbrowser.open = lambda *args: post(redir_url, data=frag.encode())

    def _tear_down(self):
        rmdir(DATA_HOME, True)

    def test_auth_success(self):
        self._setup(f'#access_token={self.token}&foo=bar')
        token = OAuth.get_token(DATA_HOME, CLIENT_ID, TEST_ADDR, 50000)
        assert token == self.token
        self._tear_down()

    def test_auth_success_second(self):
        self._setup(f'#foo=baz&access_token={self.token}&oo=bar')
        token = OAuth.get_token(DATA_HOME, CLIENT_ID, TEST_ADDR, 50000)
        assert token == self.token
        self._tear_down()

    def test_auth_fail_empty(self):
        self._setup(f'#access_token=&foo=bar')
        with pytest.raises(AuthError):
            OAuth.get_token(DATA_HOME, CLIENT_ID, TEST_ADDR, 50000)
        self._tear_down()

    def test_auth_fail_no(self):
        self._setup(f'cess_token=&foo=bar')
        with pytest.raises(AuthError):
            OAuth.get_token(DATA_HOME, CLIENT_ID, TEST_ADDR, 50000)
        self._tear_down()

    def test_auth_read_cache(self):
        rmdir(DATA_HOME, True)
        DATA_HOME.mkdir(parents=True)
        token_file = DATA_HOME / 'token'
        token_file.touch()
        token_file.write_text('foo')
        assert OAuth.get_token(DATA_HOME, CLIENT_ID, '', 0, 0) == 'foo'
        self._tear_down()

    def test_auth_write_cache(self):
        self._setup(f'#access_token={self.token}&foo=bar')
        OAuth.get_token(DATA_HOME, CLIENT_ID, TEST_ADDR, 50000)
        assert (DATA_HOME / 'token').read_text() == self.token
        self._tear_down()
