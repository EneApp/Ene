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

"""This module contains common elements for UI."""
from contextlib import contextmanager
from typing import Any, Optional

from PySide2 import QtUiTools
from PySide2.QtCore import QFile, Qt
from PySide2.QtGui import QStandardItem
from PySide2.QtWidgets import QWidget


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


def make_checkable_item(val: Any) -> QStandardItem:
    """
    Make a checkable QStandardItem.
    Args:
        val: the item value
    Returns:
        The checkable item
    """
    item = QStandardItem(val)
    item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
    item.setData(Qt.Unchecked, Qt.CheckStateRole)
    return item
