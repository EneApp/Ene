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
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from PySide2 import QtUiTools
from PySide2.QtCore import Qt, QFile
from PySide2.QtWidgets import QApplication, QAction, QMainWindow, QWidget

QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

UI_DIR = Path(__file__).parent.parent / 'ui'
APP_NAME = 'ENE'


@contextmanager
def open_ui_file(filename: str) -> QFile:
    """
    Context manager to open a Qt ui file
    Args:
        filename: Filename of the ui file

    Returns:
        The ui file opened, and closes the file afterwards
    """
    uifile = QFile(filename)
    try:
        uifile.open(QFile.ReadOnly)
        yield uifile
    finally:
        uifile.close()


def load_ui_widget(ui_file: str, parent: Optional[QWidget] = None) -> QWidget:
    """
    Load a ui wiget from file
    Args:
        ui_file: The ui file name
        parent: The parent of that wiget

    Returns:
        The loaded ui wiget
    """
    loader = QtUiTools.QUiLoader()
    with open_ui_file(ui_file) as uifile:
        ui = loader.load(uifile, parent)
    uifile.close()
    return ui


class MainForm(QMainWindow):
    """
    Main form of the application
    """

    def __init__(self):
        """
        Initialize the ui files for the application
        """
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.main_window = load_ui_widget(str(UI_DIR / 'ene.ui'))
        self.main_window.setWindowTitle(APP_NAME)
        self.prefences_window = load_ui_widget(str(UI_DIR / 'settings.ui'))
        self.prefences_window.setWindowTitle('Prefences')
        self.setup_children()

    def setup_children(self):
        """
        Setup all the child wigets of the main window
        """
        self.act_prefences = self.main_window.findChild(QAction, '﻿action_prefences')
        assert self.act_prefences
        self.act_prefences.triggered.connect(self.prefences_window.show)

    @classmethod
    def launch(cls):
        """
        Launch the Application
        """
        app = QApplication([APP_NAME])
        form = cls()
        form.main_window.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    MainForm.launch()
