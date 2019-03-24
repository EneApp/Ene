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
from typing import Any, Iterable, List, Optional, Tuple, Union

from PySide2.QtCore import QModelIndex, QObject, QPoint, QRect, QSize, Qt
from PySide2.QtGui import QIcon, QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (
    QAction, QComboBox, QLabel, QLayout, QPushButton, QSizePolicy, QStyle, QStyleOptionViewItem,
    QStyledItemDelegate, QToolButton, QVBoxLayout,
)

from ene.constants import STREAMERS
from ene.entities import Episode


class CheckMarkDelegate(QStyledItemDelegate):
    """This subclass makes check mark appear for some reason"""

    def paint(self, painter_, option_, index_):
        """
        Renders the delegate using the given painter and style option for
        the item specified  by index.
        """
        ref_to_non_const_option = QStyleOptionViewItem(option_)
        ref_to_non_const_option.showDecorationSelected = False
        super().paint(painter_, option_, index_)


class ComboCheckbox(QObject):
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
        super().__init__()
        self.combobox = combobox if combobox else QComboBox()
        self.model = QStandardItemModel()
        self.combobox.setModel(self.model)
        self.combobox.setItemDelegate(CheckMarkDelegate())
        self.combobox.view().pressed.connect(self.handle_item_pressed)
        self.checked_items = []
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
        assert item.text() not in self.checked_items
        self.checked_items.append(item.text())

    # pylint: disable=no-self-use
    def _on_uncheck(self, item: QStandardItem):
        """
        Handles unchecking an item.

        Args:
            item: Item unchecked
        """
        item.setCheckState(Qt.Unchecked)
        assert item.text() in self.checked_items
        self.checked_items.remove(item.text())

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

        self.genres = set()

        items = [title, divider.clone(), genre_text]
        for genre in genres:
            self.genres.add(genre)
            items.append(self._make_item(genre, True))
        items.append(divider)
        items.append(tag_text)
        for tag in tags:
            items.append(self._make_item(tag, True))
        super().__init__(combobox, items)
        self.combobox.setCurrentText('Genres & Tags')

    def genre_tags(self) -> Tuple[List[str], List[str]]:
        """
        Get selected genres and tags

        Returns:
            Selected genres and tags
        """
        genres, tags = [], []
        for text in self.checked_items:
            if text in self.genres:
                genres.append(text)
            else:
                tags.append(text)
        return genres, tags


class StreamerSelector(ComboCheckbox):
    """Combo checkbox to select streaming services"""

    def __init__(self, combobox: QComboBox):
        items = deque(self._make_item(val, True) for val in STREAMERS)
        streaming_on = 'Streaming On'
        items.appendleft(self._make_item('-' * (len(streaming_on) + 2), False))
        items.appendleft(self._make_item(streaming_on, False))
        super().__init__(combobox, items)
        self.combobox.setCurrentText(streaming_on)


class ToggleToolButton(QObject):
    """A toggleable tool button"""

    def __init__(self, button: Optional[QToolButton] = None):
        """
        Initialize instance

        Args:
            button: The underlying tool button
        """
        super().__init__()
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


class EpisodeButton(QPushButton):
    """Button that represents a local episode file."""

    def __init__(self, episode: Episode):
        super().__init__(episode.name)

        self.episode = episode
        if episode.state is Episode.State.WATCHED:
            self.setIcon(QIcon.fromTheme('emblem-default'))
        elif episode.state is Episode.State.NEW:
            self.setIcon(QIcon.fromTheme('emblem-important'))
        elif episode.state is Episode.State.UNWATCHED:
            self.setIcon(QIcon.fromTheme('media-optical'))
        self.setToolTip(episode.state.name.title())

    def mark_watched(self):
        self.episode.update_state(Episode.State.WATCHED)
        #  episode_model = EpisodeModel.get_by_id(self.episode.key)
        #  episode_model.state = self.episode.state.value
        #  episode_model.save()

        self.setIcon(QIcon.fromTheme('emblem-default'))
        self.setToolTip(self.episode.state.name.title())


class FlowLayout(QLayout):
    """
    A grid like layout that goes from top left to bottom right.

    Adapted from `PySide2.examples.widgets.layouts.flowlayout`
    """

    def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
        super(FlowLayout, self).__init__(parent)
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        del self._items[:]

    def addItem(self, item):  # pylint: disable=all
        self._items.append(item)

    @property
    def horizontal_spacing(self):  # pylint: disable=all
        if self._hspacing >= 0:
            return self._hspacing
        else:
            return self.smart_spacing(QStyle.PM_LayoutHorizontalSpacing)

    @property
    def vertical_spacing(self):  # pylint: disable=all
        if self._vspacing >= 0:
            return self._vspacing
        else:
            return self.smart_spacing(QStyle.PM_LayoutVerticalSpacing)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def __iter__(self):
        return iter(self._items)

    def count(self):  # pylint: disable=all
        return len(self)

    def itemAt(self, index):  # pylint: disable=all
        return self[index]

    def takeAt(self, index):  # pylint: disable=all
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):  # pylint: disable=all
        return Qt.Orientations(0)

    def hasHeightForWidth(self):  # pylint: disable=all
        return True

    def heightForWidth(self, width):  # pylint: disable=all
        return self.do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):  # pylint: disable=all
        super(FlowLayout, self).setGeometry(rect)
        self.do_layout(rect, False)

    def sizeHint(self):  # pylint: disable=all
        return self.minimumSize()

    def minimumSize(self):  # pylint: disable=all
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def do_layout(self, rect, test_only):  # pylint: disable=all
        left, top, right, bottom = self.getContentsMargins()
        effective = rect.adjusted(+left, +top, -right, -bottom)
        x = effective.x()
        y = effective.y()
        line_height = 0
        for item in self:
            widget = item.widget()
            hspace = self.horizontal_spacing
            if hspace == -1:
                hspace = widget.style().layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton, Qt.Horizontal
                )
            vspace = self.vertical_spacing
            if vspace == -1:
                vspace = widget.style().layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton, Qt.Vertical
                )
            next_x = x + item.sizeHint().width() + hspace
            if next_x - hspace > effective.right() and line_height > 0:
                x = effective.x()
                y = y + line_height + vspace
                next_x = x + item.sizeHint().width() + hspace
                line_height = 0
            if not test_only:
                item.setGeometry(
                    QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y() + bottom

    def smart_spacing(self, pm):  # pylint: disable=all
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()


class SeriesButton(QPushButton):
    def __init__(self, series, episodes):
        super().__init__()
        self.title = series
        self.setObjectName(series)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.image_frame = QLabel()
        layout = QVBoxLayout()
        self.image_frame.setLayout(layout)
        layout.setAlignment(Qt.AlignBottom)
        title_label = QLabel(series)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        self.episodes_label = QLabel('Episodes: ' + str(episodes))
        layout.addWidget(self.episodes_label)
        self.setMinimumWidth(200)
        self.setMinimumHeight(200)
        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(1, 1, 1, 1)
        base_layout.addWidget(self.image_frame)
        super().setLayout(base_layout)

    def add_action(self, label, callback):
        action = QAction(self)
        action.setText(label)
        action.triggered.connect(callback)
        self.addAction(action)

    def set_image(self, image):
        self.image_frame.setPixmap(image)

    def update_episode_count(self, count):
        self.episodes_label.setText('Episodes: ' + str(count))
