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
from PySide2.QtGui import QStandardItem
from PySide2.QtWidgets import (
    QFileDialog,
    QMainWindow,
)

from ene.constants import APP_NAME, IS_WIN
from ene.ui.common import make_checkable_item
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

        # TODO clean up
        # TODO add caching
        # TODO add threading
        title = QStandardItem('Genres & Tags')
        title.setFlags(~Qt.ItemIsUserCheckable & ~Qt.ItemIsSelectable)
        genres = self.app.api.get_genres()
        tags = [tag['name'] for tag in self.app.api.get_tags()]
        max_length = max((max(len(g) for g in genres), max(len(t) for t in tags)))
        genre_text = QStandardItem('Genres')
        genre_text.setFlags(~Qt.ItemIsUserCheckable & ~Qt.ItemIsSelectable)
        divider = QStandardItem('-' * max_length)
        divider.setFlags(~Qt.ItemIsUserCheckable & ~Qt.ItemIsSelectable)
        items = [title, divider.clone(), genre_text]
        for genre in genres:
            items.append(make_checkable_item(genre))
        tag_text = QStandardItem('Tags')
        tag_text.setFlags(~Qt.ItemIsUserCheckable & ~Qt.ItemIsSelectable)
        items.append(divider)
        items.append(tag_text)
        for tag in tags:
            items.append(make_checkable_item(tag))
        self.combobox_genre_tag = ComboCheckbox(self.combobox_genre_tag, items)
        self.combobox_genre_tag.combobox.setCurrentText('Genres & Tags')

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
