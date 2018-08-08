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

from contextlib import contextmanager
from typing import Dict, List, Optional

from PySide2 import QtUiTools
from PySide2.QtCore import QFile
from PySide2.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QWidget


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
        ref_to_non_const_option = QStyleOptionViewItem(option_)
        ref_to_non_const_option.showDecorationSelected = False
        super().paint(painter_, option_, index_)


class ChildFinderMixin:
    """Mixin class that provides child finding functions"""

    def _set_child(self, name: str, parent: str):
        """
        Set ``self``'s attribute with name ``name``
        to a QObject with the same name
        Args:
            name: Name of the object
            parent: Parent of the object

        Raises:
            RunTimeError if name is not found
        """
        parent = getattr(self, parent)
        typ = self.__annotations__[name]
        child = parent.findChild(typ, name)
        if not child:
            raise RuntimeError(
                f'Could not find child "{name}" in '
                f'{parent.windowTitle() or str(parent)}'
            )
        setattr(self, name, child)

    def _setup_children(self, children: Dict[str, List[str]]):
        """
        Setup all the child widgets of the main window
        Args:
            children: Dictionary of parents and children
        """
        for parent, names in children.items():
            for name in names:
                self._set_child(name, parent)
