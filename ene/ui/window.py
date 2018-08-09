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

"""This module contains common window classes/functions."""

from typing import Dict, List

import ene.ui
from ene.constants import resources
from .common import load_ui_widget


class UIWindowMixin:
    """Mixin class that represents a window from a ui file"""

    def __init__(self, app, ui_file: str, *args, **kwargs):
        self.app = app
        with resources.path(ene.ui, ui_file) as path:
            self.window = load_ui_widget(path)
        super().__init__(*args, **kwargs)


class ChildFinderMixin:
    """Mixin class that provides child finding functions"""

    def __init__(self, children, *args, **kwargs):
        self._setup_children(children)
        super().__init__(*args, **kwargs)

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
        parent_widget = getattr(self, parent)
        typ = self.__annotations__[name]
        child = parent_widget.findChild(typ, name)
        if not child:
            raise RuntimeError(
                f'Could not find child "{name}" in '
                f'{parent_widget.windowTitle() or str(parent_widget)}'
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


class ParentWindow(UIWindowMixin, ChildFinderMixin):
    """A UI window from file with children"""
