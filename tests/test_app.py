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

from ene.api import API

webbrowser.open = lambda *args: post(
    'http://127.0.0.1:50000',
    data=f'#access_token={MOCK_TOKEN_AUTH}'.encode()
)

from ene.ui import MainWindow, SettingsWindow
import itertools
import multiprocessing
import pytest
import toml
from requests import post
from ene.app import App, launch
from ene.constants import APP_NAME
from ene.database import Database
from . import CACHE_HOME, CONFIG_HOME, DATA_HOME, rmdir, skip_travis_osx

pytestmark = skip_travis_osx
MOCK_TOKEN_FILE = 'rm rf'
MOCK_TOKEN_AUTH = 'as'
MOCK_CONFIG = {
    'asdsa': 212312,
    'das': [1, 11]
}


def set_up_dir(dir_, exists):
    if not exists:
        rmdir(dir_, True)
    else:
        dir_.mkdir(parents=True, exist_ok=True)
        if dir_ == CONFIG_HOME:
            with open(CONFIG_HOME / 'config.toml', 'w+') as f:
                f.write(toml.dumps(MOCK_CONFIG))
        elif dir_ == DATA_HOME:
            with open(DATA_HOME / 'token', 'w+') as f:
                f.write(MOCK_TOKEN_FILE)
            Database(DATA_HOME / 'ene.db')
    return lambda: rmdir(dir_, True)


def _test_init(results, lock, cfg_exist, data_exist, cache_exist):
    with lock:
        API.query = lambda *args, **kwargs: {}
        app = App(CONFIG_HOME, DATA_HOME, CACHE_HOME)
        results.append((True, app.config_home.is_dir(), 'True,app.config_home.is_dir()'))
        results.append((True, app.data_home.is_dir(), 'True,app.data_home.is_dir()'))
        results.append((True, app.cache_home.is_dir(), 'True,app.cache_home.is_dir()'))
        results.append((APP_NAME, app.applicationName(), 'APP_NAME, app.applicationName()'))
        results.append(
            (APP_NAME, app.applicationDisplayName(), 'APP_NAME, app.applicationDisplayName()')
        )
        if cfg_exist:
            results.append((MOCK_CONFIG, dict(app.config), 'MOCK_CONFIG, dict(app.config)'))
        else:
            results.append((app.config.DEFAULT_CONFIG, dict(app.config),
                            'app.config.DEFAULT_CONFIG, dict(app.config)'))
        if data_exist:
            results.append((MOCK_TOKEN_FILE, app.api.token, 'MOCK_TOKEN_FILE, app.api.token'))
        else:
            results.append((MOCK_TOKEN_AUTH, app.api.token, 'MOCK_TOKEN_AUTH, app.api.token'))

        results.append(
            (True, isinstance(app.main_window, MainWindow),
             'True, isinstance(app.main_window, MainWindow)')
        )
        results.append(
            (True, isinstance(app.settings_window, SettingsWindow),
             'True, isinstance(app.settings_window, SettingsWindow)')
        )

        results.append(
            (True, app.settings_window.isHidden(), 'True, app.settings_window.isHidden()')
        )
        app.main_window.action_prefences.trigger()
        results.append(
            (False, app.settings_window.isHidden(), 'False, app.settings_window.isHidden()')
        )


@pytest.mark.parametrize(
    'cfg_exist,data_exist,cache_exist',
    set(itertools.permutations((True, False) * 3, 3))
)
def test_init(cfg_exist, data_exist, cache_exist):
    teardowns = [set_up_dir(CONFIG_HOME, cfg_exist),
                 set_up_dir(DATA_HOME, data_exist),
                 set_up_dir(CACHE_HOME, cache_exist)]
    with multiprocessing.Manager() as manager:
        results = manager.list()
        lock = manager.RLock()
        proc = multiprocessing.Process(
            target=_test_init,
            args=(results, lock, cfg_exist, data_exist, cache_exist)
        )
        proc.start()
        proc.join()
        for expected, actual, msg in results:
            assert expected == actual, msg
        assert proc.exitcode == 0
    for tear in teardowns:
        tear()


def test_launch():
    assert launch(CONFIG_HOME, DATA_HOME, CACHE_HOME, True) == 0
