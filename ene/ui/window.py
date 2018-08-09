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

    def __init__(self, parent, *args, **kwargs):
        if isinstance(parent, str):
            parent = getattr(self, parent)
        self._find_children(parent)
        super().__init__(*args, **kwargs)

    def _find_children(self, parent):
        """
        Setup all the child widgets of the main window
        """
        children = parent.children()
        for child in children:
            name = child.objectName()
            if name:
                setattr(self, name, child)
            self._find_children(child)


class ParentWindow(UIWindowMixin, ChildFinderMixin):
    """A UI window from file with children"""
