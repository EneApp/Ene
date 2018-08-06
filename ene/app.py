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
from PySide2.QtCore import QFile, Qt
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QFileDialog,
    QMainWindow,
    QSlider,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTabWidget,
    QToolButton,
    QWidget
)

import ene.ui
from ene.api import API
from ene.config import Config
from ene.constants import APP_NAME, IS_37, IS_WIN
from ene.util import open_source_code

if IS_37:
    from importlib import resources
else:
    import importlib_resources as resources

QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)


@contextmanager
def open_ui_file(filename: str) -> QFile:
    """
    Context manager to open a Qt ui file
    Args:
        filename: Filename of the ui file

    Returns:
        The ui file opened, and closes the file afterwards
    """
    uifile = QFile(str(filename))
    try:
        uifile.open(QFile.ReadOnly)
        yield uifile
    finally:
        uifile.close()


def load_ui_widget(ui_file: str, parent: Optional[QWidget] = None) -> QWidget:
    """
    Load a ui widget from file
    Args:
        ui_file: The ui file name
        parent: The parent of that widget

    Returns:
        The loaded ui widget
    """
    loader = QtUiTools.QUiLoader()
    with open_ui_file(ui_file) as uifile:
        ui = loader.load(uifile, parent)
    uifile.close()
    return ui


class CheckmarkDelegate(QStyledItemDelegate):
    """This subclass makes checkmark appear for some reason"""

    def paint(self, painter_, option_, index_):
        refToNonConstOption = QStyleOptionViewItem(option_)
        refToNonConstOption.showDecorationSelected = False
        super().paint(painter_, option_, index_)


class MainForm(QMainWindow):
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

    def __init__(self):
        """
        Initialize the ui files for the application
        """
        super().__init__()
        self.config = Config()
        self.api = API()
        self.setWindowTitle(APP_NAME)

        with resources.path(ene.ui, 'ene.ui') as p:
            self.main_window = load_ui_widget(p)
        with resources.path(ene.ui, 'settings.ui') as p:
            self.prefences_window = load_ui_widget(p)

        self.main_window.setWindowTitle(APP_NAME)
        self.prefences_window.setWindowTitle('Preferences')

        self.setup_children()

    def _set_child(self, name: str, parent: QWidget):
        """
        Set ``self``'s attribute with name ``name``
        to a QObject with the same name
        Args:
            name: Name of the object
            parent: Parent of the object

        Raises:
            RunTimeError if name is not found
        """
        typ = self.__annotations__[name]
        child = parent.findChild(typ, name)
        if not child:
            raise RuntimeError(
                f'Could not find child "{name}" in '
                f'{parent.windowTitle() or str(parent)}'
            )
        setattr(self, name, child)

    def setup_children(self):
        """Setup all the child widgets of the main window"""
        sc = self._set_child

        sc('action_prefences', self.main_window)
        sc('action_open_folder', self.main_window)
        sc('action_source_code', self.main_window)

        sc('widget_tab', self.main_window)

        sc('combobox_season', self.widget_tab)
        sc('combobox_sort', self.widget_tab)
        sc('combobox_format', self.widget_tab)
        sc('combobox_status', self.widget_tab)
        sc('combobox_streaming', self.widget_tab)
        sc('combobox_genre_tag', self.widget_tab)

        sc('slider_year', self.widget_tab)

        sc('button_sort_order', self.widget_tab)

        self.action_prefences.triggered.connect(self.prefences_window.show)
        self.action_open_folder.triggered.connect(self.choose_dir)
        self.action_source_code.triggered.connect(open_source_code)

        # TODO: make real items
        model = QStandardItemModel()
        for i in range(3):
            item = QStandardItem(str(i))
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
            model.setItem(i, 0, item)
        self.combobox_genre_tag.setModel(model)
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
