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
from pathlib import Path
from typing import Any, Iterable, List, Optional, Union

from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QPixmap, QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QToolButton,
    QVBoxLayout,
    QWidget
)

from ene.api import MediaFormat
from ene.constants import STREAMERS


class CheckmarkDelegate(QStyledItemDelegate):
    """This subclass makes checkmark appear for some reason"""

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
            checkable: Wether the item is checkable

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
    """A toggable tool button"""

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
    policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

    def __init__(self, fix_w=None, fix_h=None, font_size=None, stylesheet=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
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


class MediaDisplay(QWidget):

    def __init__(
            self,
            anime_id: int,
            image_path: Union[Path, str],
            title: str,
            studio: str,
            next_airing_episode: dict,
            media_format: MediaFormat,
            score: int,
            description: str,
            genres: List[str],
            *args,
            **kwargs
    ):
        # TODO: Refactor this shit
        super().__init__(*args, **kwargs)
        self.master_layout = QHBoxLayout()
        self.setLayout(self.master_layout)
        self.left_layout = QBoxLayout(QBoxLayout.BottomToTop)
        self.right_layout = QVBoxLayout()
        self.right_mid_layout = QHBoxLayout()
        self.bottom_right_layout = QHBoxLayout()

        quad_0 = 0, 0, 0, 0
        transparent_grey = 'rgba(43,48,52,0.75)'
        aqua = '#3DB4F2'
        dark_grey = '#13171D'
        grey = '#191D26'
        light_grey = '#1F232D'
        dark_white = '#818C99'
        light_white = '#9FADBD'

        self.master_layout.setSpacing(0)
        self.master_layout.setContentsMargins(*quad_0)
        self.left_layout.setSpacing(0)
        self.left_layout.setContentsMargins(*quad_0)
        self.right_mid_layout.setSpacing(0)
        self.right_mid_layout.setContentsMargins(*quad_0)
        self.right_layout.setSpacing(0)
        self.right_layout.setContentsMargins(*quad_0)
        self.bottom_right_layout.setSpacing(0)
        self.bottom_right_layout.setContentsMargins(*quad_0)

        self.image_w, self.image_h = 230, 315
        self.setFixedWidth(self.image_w * 2)
        self.setFixedHeight(self.image_h)
        self.image = QPixmap(str(image_path)).scaled(
            self.image_w, self.image_h, Qt.KeepAspectRatio
        )

        v_spacer = QSpacerItem(self.image_w, self.image_h)

        self.left_widget = QLabel()
        self.left_widget.setPixmap(self.image)
        self.left_widget.setGeometry(0, 0, self.image_w, self.image_h)

        self.left_widget.setLayout(self.left_layout)
        self.master_layout.addWidget(self.left_widget)
        self.master_layout.addLayout(self.right_layout)

        self.anime_id = anime_id
        self.title = title
        self.studio = studio
        stylesheet_template = """QLabel {
            color: %s;
            background-color: %s;
            padding: %s;
            qproperty-alignment: '%s';
            qproperty-wordWrap: true;
        }"""

        self.studio_label = FlexLabel(
            fix_w=self.image_w,
            font_size=12,
            stylesheet=stylesheet_template % (
                aqua,
                transparent_grey,
                '10px 0px 10px 10px',
                'AlignVCenter | AlignLeft'
            ),
            text=self.studio,
        )
        self.title_label = FlexLabel(
            fix_w=self.image_w,
            font_size=14,
            stylesheet=stylesheet_template % (
                'White',
                transparent_grey,
                '10px 10px 0px 10px',
                'AlignVCenter | AlignLeft'
            ),
            text=self.title,
        )
        self.left_layout.addWidget(self.studio_label)
        self.left_layout.addWidget(self.title_label)
        self.left_layout.addItem(v_spacer)

        next_episode = next_airing_episode.get('episode')
        time_until = next_airing_episode.get('timeUntilAiring')
        days, seconds = divmod(time_until, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes = seconds // 60
        time_parts = []
        if days:
            time_parts.append(f'{days}d')
        if hours:
            time_parts.append(f'{hours}h')
        time_parts.append(f'{minutes}m')
        time_str = ' '.join(time_parts)

        self.next_airing_label = QLabel()
        font = self.next_airing_label.font()
        font.setPointSize(11)
        self.next_airing_label.setFont(font)
        # TODO handle when there's no next airing
        self.next_airing_label.setText(f'Ep {next_episode} - {time_str}')
        self.next_airing_label.setStyleSheet(
            stylesheet_template % (
                aqua, dark_grey, '5px', 'AlignVCenter | AlignCenter')
        )
        self.right_layout.addWidget(self.next_airing_label)
        self.right_layout.addLayout(self.right_mid_layout)

        self.format_label = QLabel(media_format.name)
        self.format_label.setFont(font)
        self.format_label.setStyleSheet(
            stylesheet_template % (
                dark_white, grey, '5px', 'AlignVCenter | AlignCenter'
            )
        )

        # TODO handle when there's no score
        self.score_label = QLabel(f'{score}%')
        self.score_label.setFont(font)
        self.score_label.setStyleSheet(
            stylesheet_template % (
                dark_white, grey, '5px', 'AlignVCenter | AlignCenter'
            )
        )
        self.right_mid_layout.addWidget(self.format_label)
        self.right_mid_layout.addWidget(self.score_label)
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet(
            stylesheet_template % (
                dark_white, light_grey, '5px', 'AlignLeft'
            ),
        )
        self.desc_scroll = QScrollArea()
        self.desc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.desc_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.desc_scroll.setWidgetResizable(True)
        self.desc_scroll.setStyleSheet('border: none;')

        self.desc_scroll.setWidget(self.desc_label)
        self.right_layout.addWidget(self.desc_scroll)

        # TODO Need to show buttons on hover
        self.genre_label = QLabel(' '.join(genres))
        self.genre_label.setStyleSheet(
            stylesheet_template % (
                dark_white, grey, '5px', 'AlignVCenter | AlignCenter'
            )
        )
        self.bottom_right_layout.addWidget(self.genre_label)
        self.right_layout.addWidget(self.genre_label)

    def _title_studio_label(self, text, stylesheet):
        pass

    def __hash__(self):
        return hash(self.anime_id)
