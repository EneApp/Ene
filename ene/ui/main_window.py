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

"""This module contains the main window."""
from pathlib import Path

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFileDialog,
    QMainWindow,
)

from ene.constants import APP_NAME, IS_WIN
from ene.util import open_source_code
from .custom import ComboCheckbox
from .window import ParentWindow


class MainWindow(ParentWindow, QMainWindow):
    """
    Main form of the application
    """

    def __init__(self, app):
        """
        Initialize the ui files for the application
        """
        super().__init__(app, 'main_window.ui', 'window')
        self.window.setWindowTitle(APP_NAME)
        self.setWindowTitle(APP_NAME)
        self._setup_children()

    def _setup_children(self):
        """Setup all the child widgets of the main window"""
        self.action_open_folder.triggered.connect(self.choose_dir)
        self.action_source_code.triggered.connect(open_source_code)
        self.combobox_genre_tag = ComboCheckbox(self.combobox_genre_tag, ['1', '2', '3'])
        self.combobox_genre_tag.combobox.view().pressed.connect(self.handle_item_pressed)

    def handle_item_pressed(self, index):
        """
        Handles a checkable item being pressed in a combo box
        Args:
            index: Index of the item
        """
        print(index)
        item = self.combobox_genre_tag.combobox.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def choose_dir(self) -> Path:
        """
        Choose a directory from a file dialog

        Returns: The directory path
        """
        args = [self, self.tr("Open Directory"), str(Path.home())]
        if IS_WIN:
            args.append(QFileDialog.DontUseNativeDialog)
        dir_ = QFileDialog.getExistingDirectory(*args)
        # TODO do something with this
        return Path(dir_)
