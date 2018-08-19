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

from os import environ
from pathlib import Path

environ['XDG_CONFIG_HOME'] = str(Path(__file__).parent.resolve())

import pytest
from toml import dump, loads
from . import rmdir
from ene.config import Config
from ene.constants import CONFIG_HOME

CONFIG_FILE = CONFIG_HOME / 'config.toml'

MOCK_SETTINGS = {
    'foo': 1,
    'bar': 'baz',
    'qux': {
        'y': 'tt',
        'sad': ['foo', 'bar']
    }
}


@pytest.fixture()
def path():
    rmdir(CONFIG_HOME, True)
    CONFIG_HOME.mkdir(parents=True)
    with CONFIG_FILE.open('w+') as f:
        dump(MOCK_SETTINGS, f)
    yield CONFIG_HOME
    rmdir(CONFIG_HOME, False)


@pytest.fixture()
def path_empty():
    rmdir(CONFIG_HOME, True)
    yield CONFIG_HOME
    rmdir(CONFIG_HOME, False)


def test_config_read(path):
    cfg = Config()
    assert loads(CONFIG_FILE.read_text()) == cfg.config
    assert loads(CONFIG_FILE.read_text()) != cfg.DEFAULT_CONFIG


def test_config_read_default(path_empty):
    cfg = Config()
    assert loads(CONFIG_FILE.read_text()) == cfg.config
    assert cfg.config == Config.DEFAULT_CONFIG


def test_write_fail(path):
    cfg = Config()
    test_data = MOCK_SETTINGS.copy()
    with pytest.raises(TypeError):
        cfg['asd'] = 2121
    assert loads(CONFIG_FILE.read_text()) == test_data


def test_config_write(path):
    cfg = Config()
    test_data = MOCK_SETTINGS.copy()
    test_data['asd'] = 2121
    with cfg.change() as cg:
        cg['asd'] = 2121
        cfg.apply()
    assert loads(CONFIG_FILE.read_text()) == test_data
    assert cfg['asd'] == test_data['asd']


def test_config_write_default(path_empty):
    cfg = Config()
    test_data = cfg.DEFAULT_CONFIG.copy()
    test_data['asd'] = 2121
    with cfg.change() as cg:
        cg['asd'] = 2121
        cfg.apply()
    assert loads(CONFIG_FILE.read_text()) == test_data
    assert cfg['asd'] == test_data['asd']


def test_config_write_revert(path):
    cfg = Config()
    test_data = MOCK_SETTINGS.copy()
    with cfg.change() as cg:
        cg['asd'] = 2121
    assert loads(CONFIG_FILE.read_text()) == test_data
