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

"""This module contains the main application class."""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import qdarkstyle
from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QApplication

from .api import API
from .config import Config
from .constants import APP_NAME, CACHE_HOME, CONFIG_HOME, DATA_HOME
from .ui import MainWindow, SettingsWindow

QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)


class App(QApplication):
    """Main Application class"""

    def __init__(self, config_home: Path, data_home: Path, cache_home: Path):
        """
        Args:
            config_home:
            data_home:
            cache_home:
        """
        args = [APP_NAME]
        args.extend(sys.argv[1:])
        super().__init__(args)
        self.config_home = config_home
        self.data_home = data_home
        self.cache_home = cache_home
        for path in (self.config_home, self.data_home, self.cache_home):
            path.mkdir(parents=True, exist_ok=True)
        self.config = Config(config_home)
        self.pool = ThreadPoolExecutor()
        self.api = API(data_home)
        self.main_window = MainWindow(self)
        self.settings_window = SettingsWindow(self)
        self.main_window.action_prefences.triggered.connect(self.settings_window.show)


def launch(config_home=CONFIG_HOME, data_home=DATA_HOME, cache_home=CACHE_HOME, test=False):
    """
    Launch the Application

    Args:
        config_home:
        data_home:
        cache_home:
        test: True to use test mode, default False
    """
    if test:
        API.query = lambda *args, **kwargs: {}
    app = App(config_home, data_home, cache_home)
    if test:
        QTimer.singleShot(5000, app.quit)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())
    app.main_window.show()
    return app.exec_()
