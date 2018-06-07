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

import webbrowser
from secrets import token_urlsafe

import pytest
from requests import post

from ene.api import APIAuthError, OAuth

CLIENT_ID = 0
TEST_ADDR = '127.0.0.1'


class TestAuth:
    token = token_urlsafe()

    def _setup(self, frag):
        redir_url = f'http://127.0.0.1:50000'
        webbrowser.open = lambda *args: post(redir_url, data=frag.encode())

    def test_auth_success(self):
        self._setup(f'#access_token={self.token}&foo=bar')
        token = OAuth.get_token(CLIENT_ID, TEST_ADDR, 50000)
        assert token == self.token

    def test_auth_success_second(self):
        self._setup(f'#foo=baz&access_token={self.token}&oo=bar')
        token = OAuth.get_token(CLIENT_ID, TEST_ADDR, 50000)
        assert token == self.token

    def test_auth_fail_empty(self):
        self._setup(f'#access_token=&foo=bar')
        with pytest.raises(APIAuthError):
            OAuth.get_token(CLIENT_ID, TEST_ADDR, 50000)

    def test_auth_fail_no(self):
        self._setup(f'cess_token=&foo=bar')
        with pytest.raises(APIAuthError):
            OAuth.get_token(CLIENT_ID, TEST_ADDR, 50000)
