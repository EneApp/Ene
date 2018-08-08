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

from pathlib import Path

from PySide2.QtCore import Qt
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (
    QAction,
    QComboBox,
    QFileDialog,
    QMainWindow,
    QSlider,
    QTabWidget,
    QToolButton,
)

from ene.constants import APP_NAME, IS_WIN
from ene.util import open_source_code
from .common import CheckmarkDelegate, ParentWindow


class MainWindow(ParentWindow, QMainWindow):
    """
    Main form of the application
    """

    action_prefences: QAction
    action_open_folder: QAction
    action_source_code: QAction
    widget_tab: QTabWidget

    combobox_season: QComboBox
    combobox_sort: QComboBox
    combobox_format: QComboBox
    combobox_status: QComboBox
    combobox_streaming: QComboBox
    combobox_genre_tag: QComboBox

    slider_year: QSlider
    button_sort_order: QToolButton

    def __init__(self, app):
        """
        Initialize the ui files for the application
        """
        children = {
            'window': [
                'action_prefences',
                'action_open_folder',
                'action_source_code',
                'widget_tab',
            ],
            'widget_tab': [
                'combobox_season',
                'combobox_sort',
                'combobox_format',
                'combobox_status',
                'combobox_streaming',
                'combobox_genre_tag',
                'slider_year',
                'button_sort_order',
            ],
        }
        super().__init__(app, 'main_window.ui', children)
        self.window.setWindowTitle(APP_NAME)
        self.setWindowTitle(APP_NAME)

    def _setup_children(self, children):
        """Setup all the child widgets of the main window"""
        super()._setup_children(children)
        self.action_open_folder.triggered.connect(self.choose_dir)
        self.action_source_code.triggered.connect(open_source_code)

        # TODO: make real items
        genre_model = QStandardItemModel()
        for i in range(3):
            item = QStandardItem(str(i))
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            genre_model.setItem(i, 0, item)
        self.combobox_genre_tag.setModel(genre_model)
        self.combobox_genre_tag.setItemDelegate(CheckmarkDelegate())
        self.combobox_genre_tag.view().pressed.connect(self.handle_item_pressed)

    def handle_item_pressed(self, index):
        """
        Handles a checkable item being pressed in a combo box
        Args:
            index: Index of the item
        """
        item = self.combobox_genre_tag.model().itemFromIndex(index)
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
