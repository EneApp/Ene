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

"""This module contains custom UI widgets/elements."""
from collections import deque
from itertools import chain
from typing import Any, Iterable, Optional, Union

from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (
    QComboBox,
    QLabel,
    QSizePolicy,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QToolButton,
)

from ene.constants import STREAMERS


class CheckmarkDelegate(QStyledItemDelegate):
    """This subclass makes check mark appear for some reason"""

    def paint(self, painter_, option_, index_):
        """
        Renders the delegate using the given painter and style option for
        the item specified  by index.
        """
        ref_to_non_const_option = QStyleOptionViewItem(option_)
        ref_to_non_const_option.showDecorationSelected = False
        super().paint(painter_, option_, index_)


class ComboCheckbox:
    """A combo box with its items as checkboxes."""

    def __init__(
            self,
            combobox: Optional[QComboBox],
            items: Optional[Iterable[QStandardItem]] = None
    ):
        """
        Initialize instance

        Args:
            combobox: The underlying combobox, None to create a new one
            items: Items to put in the combobox, if any
        """
        self.combobox = combobox if combobox else QComboBox()
        self.model = QStandardItemModel()
        self.combobox.setModel(self.model)
        self.combobox.setItemDelegate(CheckmarkDelegate())
        self.combobox.view().pressed.connect(self.handle_item_pressed)
        if items:
            self.model.appendColumn(items)

    @staticmethod
    def _make_item(val: Any, checkable: bool) -> QStandardItem:
        """
        Make an item for the combobox

        Args:
            val: The value for the item
            checkable: Whether the item is checkable

        Returns:
            The item created
        """
        item = QStandardItem(val)
        if checkable:
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
        else:
            item.setFlags(~Qt.ItemIsUserCheckable & ~Qt.ItemIsSelectable)
        return item

    # pylint: disable=no-self-use
    def _on_check(self, item: QStandardItem):
        """
        Handles checking an item.

        Args:
            item: Item checked
        """
        item.setCheckState(Qt.Checked)

    # pylint: disable=no-self-use
    def _on_uncheck(self, item: QStandardItem):
        """
        Handles unchecking an item.

        Args:
            item: Item unchecked
        """
        item.setCheckState(Qt.Unchecked)

    def __getitem__(self, i: Union[int, QModelIndex]) -> QStandardItem:
        """
        Get item by index

        Args:
            i: The index
        Returns:
            Item at the index
        Raises:
            IndexError if out of bounds
        """
        if isinstance(i, int):
            if i < 0:
                i = len(self) - i
            if i >= len(self):
                raise IndexError
            index = self.model.createIndex(i, 0)
        elif isinstance(i, QModelIndex):
            if i.row() >= len(self):
                raise IndexError
            index = i
        else:
            return NotImplemented
        return self.model.itemFromIndex(index)

    def __len__(self):
        return self.combobox.count()

    def handle_item_pressed(self, index):
        """
        Handles a checkable item being pressed in a combo box

        Args:
            index: Index of the item
        """
        item = self[index]
        if item.isCheckable():
            if item.checkState() == Qt.Checked:
                self._on_uncheck(item)
            else:
                self._on_check(item)


class GenreTagSelector(ComboCheckbox):
    """Class for the genres/tags selector."""

    def __init__(self, combobox: QComboBox, genres: Iterable[str], tags: Iterable[str]):
        """
        Initialize instance

        Args:
            combobox: The underlying combobox
            genres: List of genre names
            tags: List of tag names
        """
        max_length = max(chain(map(len, genres), map(len, tags)))
        title = self._make_item('Genres & Tags', False)
        tag_text = self._make_item('Tags', False)
        genre_text = self._make_item('Genres', False)
        divider = self._make_item('-' * max_length, False)

        items = [title, divider.clone(), genre_text]
        for genre in genres:
            items.append(self._make_item(genre, True))
        items.append(divider)
        items.append(tag_text)
        for tag in tags:
            items.append(self._make_item(tag, True))
        super().__init__(combobox, items)
        self.combobox.setCurrentText('Genres & Tags')


class StreamerSelector(ComboCheckbox):
    """Combo checkbox to select streaming services"""

    def __init__(self, combobox: QComboBox):
        items = deque(self._make_item(val, True) for val in STREAMERS)
        streaming_on = 'Streaming On'
        items.appendleft(self._make_item('-' * (len(streaming_on) + 2), False))
        items.appendleft(self._make_item(streaming_on, False))
        super().__init__(combobox, items)
        self.combobox.setCurrentText(streaming_on)


class ToggleToolButton:
    """A toggleable tool button"""

    def __init__(self, button: Optional[QToolButton] = None):
        """
        Initialize instance

        Args:
            button: The underlying tool button
        """
        self.button = button or QToolButton()
        self.button.clicked.connect(self._handle_toggle)

    def _on_up(self):
        """Handles when the button becomes up arrow"""
        self.button.setArrowType(Qt.UpArrow)

    def _on_down(self):
        """Handles when the button becomes down arrow"""
        self.button.setArrowType(Qt.DownArrow)

    def _handle_toggle(self):
        """Handles when the button is toggled"""
        if self.button.arrowType() == Qt.UpArrow:
            self._on_down()
        else:
            self._on_up()


class FlexLabel(QLabel):
    """A label that automatically resizes"""
    policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

    def __init__(self, fix_w=None, fix_h=None, font_size=None, stylesheet=None, **kwargs):
        """
        A label that automatically resizes

        Args:
            fix_w: Optional fixed width
            fix_h: Optional fixed height
            font_size: Optional font size
            stylesheet: Optional stylesheet
            **kwargs: Any other key word arguments that's passed to super
        """
        super().__init__(**kwargs)
        if fix_w:
            self.setFixedWidth(fix_w)
        if fix_h:
            self.setFixedHeight(fix_h)
        if font_size:
            font = self.font()
            font.setPointSize(font_size)
            self.setFont(font)
        if stylesheet:
            self.setStyleSheet(stylesheet)
        self.setSizePolicy(self.policy)
        self.setWordWrap(True)
        self.adjustSize()
