#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2019 Peijun Ma, Justin Sedge
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

"""This module contains the media browser."""
from threading import RLock
from typing import List, Optional, Tuple

from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QPixmap, QTextOption
from PySide2.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ene.api import MediaFormat, MediaSeason, MediaSort, MediaStatus
from ene.api.media import Media
from ene.ui.common import mk_padding, mk_stylesheet
from ene.ui.custom import FlowLayout, GenreTagSelector, StreamerSelector, ToggleToolButton


class MediaDisplay(QWidget):
    """A widget that displays a media in the media browser."""
    image_w = 230
    image_h = 315

    transparent_grey = 'rgba(43,48,52,0.75)'
    aqua = '#3DB4F2'
    dark_grey = '#13171D'
    grey = '#191D26'
    light_grey = '#1F232D'
    dark_white = '#818C99'
    light_white = '#9FADBD'
    lighter_white = '#EDF1F5'

    def __init__(self, media: Media, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(self.image_w * 2)
        self.setFixedHeight(self.image_h)
        self.media = media

        self._setup_layouts()
        self._setup_left()
        self._setup_airing()
        self._setup_format()
        qss = self._setup_des()
        self._setup_bottom_bar(qss)

    def set_image(self):
        """
        Set the cover image of the display
        """
        if not self.parent():
            return
        self.media.cover_image \
            .map(lambda p: QPixmap(str(p)).scaled(self.image_w, self.image_h)) \
            .map(lambda img: self.image_label.setPixmap(img))

    def _setup_layouts(self):
        self.master_layout = QHBoxLayout()
        self.setLayout(self.master_layout)

        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.right_mid_layout = QHBoxLayout()
        self.bottom_right_layout = QHBoxLayout()

        self.left_layout.setAlignment(Qt.AlignBottom)
        for layout in (
                self.master_layout,
                self.left_layout,
                self.right_layout,
                self.right_mid_layout,
                self.bottom_right_layout
        ):
            layout.setSpacing(0)
            layout.setMargin(0)

    def _setup_left(self):
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.image_w, self.image_h)
        stylesheet = {
            'color': self.lighter_white,
            'background-color': self.transparent_grey,
            'padding': '10px',
            'font-size': '14pt',
            'qproperty-wordWrap': 'true',
            'qproperty-alignment': '"AlignVCenter | AlignLeft"',
        }

        self.image_label.setLayout(self.left_layout)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.left_layout.addWidget(spacer)

        title_label = self.media.title.map_or(lambda s: QLabel(s), None)
        studio_label = self.media.studio.map_or(lambda s: QLabel(s.name), None)
        if title_label:
            title_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))
            self.left_layout.addWidget(title_label)
        if studio_label:
            stylesheet['color'] = self.aqua
            stylesheet['padding'] = mk_padding(0, 10, 10, 10)
            stylesheet['font-size'] = '12pt'
            studio_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))
            self.left_layout.addWidget(studio_label)

        self.master_layout.addWidget(self.image_label)
        self.master_layout.addLayout(self.right_layout)

    def _setup_airing(self):
        def get_airing_lbl(next_airing):
            next_episode = next_airing.episode
            time_until = next_airing.time_until_airing
            if next_episode and time_until:
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
                return QLabel(f'Ep {next_episode} - {time_str}')

        def get_season_lbl():
            year = self.media.start_date.map_or(lambda d: d.year, None)
            if self.media.season and year:
                return QLabel(f'{self.media.season.value.name.title()} {year}')
            elif year:
                return QLabel(str(year))

        next_airing_label = self.media.next_airing_episode \
            .map_or_else(get_airing_lbl, get_season_lbl)
        if next_airing_label:
            next_airing_label.setStyleSheet(mk_stylesheet({
                'color': self.aqua,
                'background-color': self.dark_grey,
                'padding': '5px',
                'font-size': '11pt',
                'qproperty-alignment': '"AlignCenter"'
            }, 'QLabel'))
            self.right_layout.addWidget(next_airing_label)
        self.right_layout.addLayout(self.right_mid_layout)

    def _setup_format(self):
        format_label = self.media.format.map(lambda f: QLabel(f.name))
        score_label = self.media.average_score.map(lambda s: QLabel(f'{s}%'))

        if not format_label and not score_label:
            return

        stylesheet = mk_stylesheet({
            'color': self.dark_white,
            'background-color': self.grey,
            'padding': '5px',
            'font-size': '11pt',
            'qproperty-alignment': '"AlignCenter"',
            'qproperty-wordWrap': 'true'
        }, 'QLabel')

        def _add(l):
            l.setStyleSheet(stylesheet)
            self.right_mid_layout.addWidget(l)

        format_label.map(_add)
        score_label.map(_add)

    def _setup_des(self):
        desc_text_edit = QTextEdit()
        self.media.description.map(lambda d: desc_text_edit.setHtml(d))
        desc_text_edit.setReadOnly(True)
        desc_text_edit.setFrameStyle(QFrame.NoFrame)
        desc_text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        desc_text_edit.setWordWrapMode(QTextOption.WordWrap)
        stylesheet = {
            'color': self.dark_white,
            'background-color': self.light_grey,
            'padding': '5px',
            'font-size': '10pt',
            'border': 'none'
        }
        desc_text_edit.setStyleSheet(mk_stylesheet(stylesheet, 'QTextEdit'))

        self.right_layout.addWidget(desc_text_edit)
        return stylesheet

    def _setup_bottom_bar(self, stylesheet):
        # TODO Need to show buttons on hover
        genre_label = QLabel(', '.join(self.media.genres))
        stylesheet['qproperty-alignment'] = '"AlignCenter"'
        stylesheet['background-color'] = self.dark_grey
        genre_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))
        self.bottom_right_layout.addWidget(genre_label)
        self.right_layout.addWidget(genre_label)


class MediaBrowser(QScrollArea):
    """This class controls the media browsing tab."""

    ctrl_ready_signal = Signal(list, list, QWidget, QWidget)
    media_ready_signal = Signal(list)

    def __init__(  # pylint: disable=R0913
            self,
            app,
            button_sort_order: QToolButton,
            combobox_season: QComboBox,
            spinbox_year_min: QSpinBox,
            spinbox_year_max: QSpinBox,
            combobox_sort: QComboBox,
            combobox_format: QComboBox,
            combobox_status: QComboBox,
            checkbox_on_list: QCheckBox,
            checkbox_adult: QCheckBox
    ):
        """
        Initialize instance

        Args:
            app: The application instance
            button_sort_order: The tool button for sort order
        """
        super().__init__()
        self.reset_media_lock = RLock()

        self.combobox_season = combobox_season
        self.spinbox_year_min = spinbox_year_min
        self.spinbox_year_max = spinbox_year_max
        self.combobox_sort = combobox_sort
        self.combobox_format = combobox_format
        self.combobox_status = combobox_status
        self.checkbox_on_list = checkbox_on_list
        self.checkbox_adult = checkbox_adult
        self._setup_ui(button_sort_order)

        self.app = app
        self.api = self.app.api

        self.current_page = 0
        self.has_next_page = True

        self.is_setup = False

        self.genre_tag_selector = None
        self.streamer_selector = None

        self._scroll_bar = self.verticalScrollBar()
        self.ctrl_ready_signal.connect(self._setup_controls)
        self.media_ready_signal.connect(self._media_ready)
        self._scroll_bar.valueChanged.connect(self._on_scroll)

    @property
    def season(self) -> Optional[MediaSeason]:
        """The season the media was initially released in."""
        return {
            'All': None,
            'Winter': MediaSeason.WINTER,
            'Spring': MediaSeason.SPRING,
            'Summer': MediaSeason.SUMMER,
            'Fall': MediaSeason.FALL
        }[self.combobox_season.currentText()]

    @property
    def year_range(self) -> Tuple[int, int]:
        """Year range of the first official release date of the media."""
        min_, max_ = self.spinbox_year_min.value(), self.spinbox_year_max.value()
        return min_, max_

    @property
    def sort(self) -> Optional[List[MediaSort]]:
        """The order the results will be displayed in."""
        res = {
            'Sort': None,
            'Popularity': 'POPULARITY',
            'Score': 'SCORE',
            'Trending': 'TRENDING',
            'Favourites': 'FAVOURITES',
            'Date Added': 'ID',
            'Release Date': 'START_DATE'
        }[self.combobox_sort.currentText()]
        if res:
            if self.sort_toggle.button.arrowType() == Qt.DownArrow:
                res = f'{res}_DESC'
            return [MediaSort[res]]
        else:
            return None

    @property
    def format(self) -> Optional[MediaFormat]:
        """The media's format."""
        return {
            'Format': None,
            'TV': MediaFormat.TV,
            'TV Short': MediaFormat.TV_SHORT,
            'Movie': MediaFormat.MOVIE,
            'Special': MediaFormat.SPECIAL,
            'OVA': MediaFormat.OVA,
            'ONA': MediaFormat.ONA,
            'Music': MediaFormat.MUSIC
        }[self.combobox_format.currentText()]

    @property
    def status(self) -> Optional[MediaStatus]:
        """The media's current release status."""
        return {
            'Status': None,
            'Releasing': MediaStatus.RELEASING,
            'Finished': MediaStatus.FINISHED,
            'Not Yet Released': MediaStatus.NOT_YET_RELEASED,
            'Cancelled': MediaStatus.CANCELLED
        }[self.combobox_status.currentText()]

    @property
    def streaming_on(self) -> Optional[List[str]]:
        """Sites with a online streaming license of the media."""
        return self.streamer_selector.checked_items or None

    @property
    def on_list(self) -> Optional[bool]:
        """Whether the media is on the authenticated user's lists."""
        if self.checkbox_on_list.isChecked():
            return False
        return None

    @property
    def adult(self) -> bool:
        """Whether if the media's intended for 18+ adult audiences."""
        return self.checkbox_adult.isChecked()

    def _setup_ui(self, button_sort_order):
        self._layout = FlowLayout(None, 10, 10, 10)
        self._layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.control_widget = QWidget()
        self.control_widget.setLayout(self._layout)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidget(self.control_widget)
        self.setWidgetResizable(True)
        self.sort_toggle = ToggleToolButton(button_sort_order)

    def fetch_control_info(self, combobox_genre_tag, combobox_streaming):
        """
        Fetch the needed control information from the anilist API and triggers
        the signal to set up control widgets

        Args:
            combobox_genre_tag: The combobox to select genres and tags
            combobox_streaming: The combobox to select streamers
        """
        genre_future = self.app.pool.submit(self.app.api.get_genres)
        tags_future = self.app.pool.submit(self.app.api.get_tags)
        tags_result = tags_future.result()
        genres_result = genre_future.result()
        if not tags_result or not genres_result:
            raise ValueError("Failed to fetch tags/genres.")
        tags = [tag['name'] for tag in tags_result.unwrap()]
        self.ctrl_ready_signal.emit(
            genres_result.unwrap(),
            tags,
            combobox_genre_tag,
            combobox_streaming
        )

    @Slot(list)
    def _media_ready(self, media_list):
        with self.reset_media_lock:
            for anime in media_list:
                if not anime:
                    continue
                display = MediaDisplay(anime)
                self._layout.addWidget(display)
                self.app.pool.submit(display.set_image)

    def get_media(self):
        """
        Get media from anilist and put them into the layout
        """
        self.app.pool.submit(self._get_media)

    def _get_media(self):
        self.current_page += 1
        genres, tags = self.genre_tag_selector.genre_tags()
        res = self.api.browse_anime(
            self.current_page,
            season=self.season,
            year_range=self.year_range,
            sort=self.sort,
            format_=self.format,
            status=self.status,
            licensed_by=self.streaming_on,
            included_genres=genres or None,
            included_tags=tags or None,
            on_list=self.on_list,
            is_adult=self.adult
        )
        if res:
            media_lst, has_next = res.unwrap()
            self.has_next_page = has_next
            self.media_ready_signal.emit(media_lst)
        else:
            self.has_next_page = False

    @Slot(list, list, QWidget, QWidget)
    def _setup_controls(self, genres, tags, combobox_genre_tag, combobox_streaming):
        self.genre_tag_selector = GenreTagSelector(combobox_genre_tag, genres, tags)
        self.streamer_selector = StreamerSelector(combobox_streaming)
        for signal in (
                self.combobox_status.currentTextChanged,
                self.combobox_format.currentTextChanged,
                self.combobox_sort.currentTextChanged,
                self.combobox_season.currentTextChanged,
                self.sort_toggle.button.clicked,
                self.spinbox_year_min.valueChanged,
                self.spinbox_year_max.valueChanged,
                self.streamer_selector.combobox.view().pressed,
                self.genre_tag_selector.combobox.view().pressed,
                self.checkbox_adult.clicked,
                self.checkbox_on_list.clicked
        ):
            signal.connect(self.reset_media)
        self.get_media()

    @Slot(int)
    def _on_scroll(self, value):
        if value == self._scroll_bar.maximum() and self.has_next_page:
            self.get_media()

    @Slot()
    def reset_media(self):
        """Reset the media display."""
        with self.reset_media_lock:
            self.current_page = 0
            self.has_next_page = False
            for item in reversed(self._layout):
                item.widget().setParent(None)
            self._layout._items.clear()  # pylint: disable=W0212
            self._scroll_bar.setValue(0)
            self.get_media()
