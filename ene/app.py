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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

from ene.api import API
from ene.config import Config
from ene.constants import APP_NAME
from ene.ui import MainWindow, SettingsWindow

QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
config = Config()


class App(QApplication):
    """Main Application class"""

    def __init__(self):
        super().__init__([APP_NAME])
        self.api = API()
        self.main_window = MainWindow(self)
        self.settings_window = SettingsWindow(self)
        self.main_window.action_prefences.triggered.connect(self.settings_window.window.show)


def launch():
    """
    Launch the Application
    """
    app = App()
    app.main_window.window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch()
