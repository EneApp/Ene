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

from PySide2.QtCore import QModelIndex, QPoint, QRect, QSize, Qt
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (
    QComboBox, QLayout, QSizePolicy, QStyle, QStyleOptionViewItem, QStyledItemDelegate,
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


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
        super(FlowLayout, self).__init__(parent)
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        del self._items[:]

    def addItem(self, item):
        self._items.append(item)

    def horizontalSpacing(self):
        if self._hspacing >= 0:
            return self._hspacing
        else:
            return self.smartSpacing(
                QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vspacing >= 0:
            return self._vspacing
        else:
            return self.smartSpacing(
                QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def doLayout(self, rect, testonly):
        left, top, right, bottom = self.getContentsMargins()
        effective = rect.adjusted(+left, +top, -right, -bottom)
        x = effective.x()
        y = effective.y()
        lineheight = 0
        for item in self._items:
            widget = item.widget()
            hspace = self.horizontalSpacing()
            if hspace == -1:
                hspace = widget.style().layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton, Qt.Horizontal)
            vspace = self.verticalSpacing()
            if vspace == -1:
                vspace = widget.style().layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + hspace
            if nextX - hspace > effective.right() and lineheight > 0:
                x = effective.x()
                y = y + lineheight + vspace
                nextX = x + item.sizeHint().width() + hspace
                lineheight = 0
            if not testonly:
                item.setGeometry(
                    QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineheight = max(lineheight, item.sizeHint().height())
        return y + lineheight - rect.y() + bottom

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
