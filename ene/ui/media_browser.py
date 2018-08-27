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

"""This module contains the media browser."""
from pathlib import Path
from typing import List, Optional

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (
    QHBoxLayout, QLabel, QLayout, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from ene.api import MediaFormat, MediaSeason
from ene.util import get_resource, strip_html
from .common import mk_padding, mk_stylesheet
from .custom import FlowLayout, GenreTagSelector, StreamerSelector, ToggleToolButton


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

    # pylint: disable=R0913,R0914
    def __init__(
            self,
            cache_home: Path,
            anime_id: int,
            image_url: str,
            title: str,
            season: MediaSeason,
            year: int,
            studio: Optional[str],
            next_airing_episode: Optional[dict],
            media_format: MediaFormat,
            score: int,
            description: str,
            genres: List[str],
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(self.image_w * 2)
        self.setFixedHeight(self.image_h)
        self.anime_id = anime_id
        image_path = str(get_resource(image_url, cache_home))

        img = QPixmap(image_path).scaled(self.image_w, self.image_h, Qt.KeepAspectRatio)

        self._setup_layouts()
        self._setup_left(img, title, studio)
        self._setup_airing(next_airing_episode, season, year)
        self._setup_format(media_format, score)
        qss = self._setup_des(description)
        self._setup_bottom_bar(genres, qss)

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

    def _setup_left(self, image, title, studio):
        left_label = QLabel()
        left_label.setPixmap(image)
        stylesheet = {
            'color': self.lighter_white,
            'background-color': self.transparent_grey,
            'padding': '10px',
            'font-size': '14pt',
            'qproperty-wordWrap': 'true',
            'qproperty-alignment': '"AlignVCenter | AlignLeft"',
        }

        title_label = QLabel(title)
        title_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))

        if studio:
            studio_label = QLabel(studio)
            stylesheet['color'] = self.aqua
            stylesheet['padding'] = mk_padding(0, 10, 10, 10)
            stylesheet['font-size'] = '12pt'
            studio_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))
        else:
            studio_label = None

        for lbl in filter(None, (title_label, studio_label)):
            lbl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        left_label.setLayout(self.left_layout)
        self.left_layout.addWidget(title_label)
        if studio_label:
            self.left_layout.addWidget(studio_label)

        self.master_layout.addWidget(left_label)
        self.master_layout.addLayout(self.right_layout)

    def _setup_airing(self, next_airing_episode, season, year):
        next_airing_episode = next_airing_episode or {}
        next_episode = next_airing_episode.get('episode')
        time_until = next_airing_episode.get('timeUntilAiring')
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
            next_airing_label = QLabel(f'Ep {next_episode} - {time_str}')
        elif season:
            next_airing_label = QLabel(f'{season.name.title()} {year}')
        else:
            next_airing_label = QLabel(str(year))

        next_airing_label.setStyleSheet(mk_stylesheet({
            'color': self.aqua,
            'background-color': self.dark_grey,
            'padding': '5px',
            'font-size': '11pt',
            'qproperty-alignment': '"AlignCenter"'
        }, 'QLabel'))
        self.right_layout.addWidget(next_airing_label)
        self.right_layout.addLayout(self.right_mid_layout)

    def _setup_format(self, media_format, score):
        format_label = QLabel(media_format.name)
        stylesheet = mk_stylesheet({
            'color': self.dark_white,
            'background-color': self.grey,
            'padding': '5px',
            'font-size': '11pt',
            'qproperty-alignment': '"AlignCenter"',
            'qproperty-wordWrap': 'true'
        }, 'QLabel')
        format_label.setStyleSheet(stylesheet)
        self.right_mid_layout.addWidget(format_label)
        if score is not None:
            score_label = QLabel(f'{score}%')
            score_label.setStyleSheet(stylesheet)
            self.right_mid_layout.addWidget(score_label)

    def _setup_des(self, description):
        desc_label = QLabel(strip_html(description))
        stylesheet = {
            'color': self.dark_white,
            'background-color': self.light_grey,
            'padding': '5px',
            'font-size': '10pt',
            'qproperty-alignment': '"AlignLeft"',
            'qproperty-wordWrap': 'true'
        }
        desc_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))
        desc_scroll = QScrollArea()
        desc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        desc_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        desc_scroll.setWidgetResizable(True)
        desc_scroll.setStyleSheet(mk_stylesheet({'border': 'none'}, 'QScrollArea'))
        desc_scroll.setWidget(desc_label)

        self.right_layout.addWidget(desc_scroll)
        return stylesheet

    def _setup_bottom_bar(self, genres, stylesheet):
        # TODO Need to show buttons on hover
        genre_label = QLabel(', '.join(genres))
        stylesheet['qproperty-alignment'] = '"AlignCenter"'
        genre_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))
        self.bottom_right_layout.addWidget(genre_label)
        self.right_layout.addWidget(genre_label)


class MediaBrowser(QScrollArea):
    """This class controls the media browsing tab."""

    def __init__(
            self,
            app,
            combobox_genre_tag,
            combobox_streaming,
            button_sort_order
    ):
        super().__init__()
        self.app = app
        self.api = self.app.api

        # genre_future = self.app.pool.submit(self.app.api.get_genres)
        # tags_future = self.app.pool.submit(self.app.api.get_tags)

        # tags = [tag['name'] for tag in tags_future.result()]
        # genres = genre_future.result()
        tags = ['']
        genres = ['']
        self.genre_tag_selector = GenreTagSelector(combobox_genre_tag, genres, tags)
        self.streamer_selector = StreamerSelector(combobox_streaming)
        self.sort_toggle = ToggleToolButton(button_sort_order)

        self._layout = FlowLayout(None, 10, 10, 10)
        self._layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.control_widget = QWidget()
        self.control_widget.setLayout(self._layout)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidget(self.control_widget)
        self.setWidgetResizable(True)

        self.get_media()

    def get_media(self, page=1):
        for anime in self.api.browse_anime(page):
            season = anime['season']
            season = MediaSeason[season] if season else None
            studios = anime['studios']['edges']
            studio = studios[0]['node']['name'] if studios else None
            self._layout.addWidget(MediaDisplay(
                cache_home=self.app.cache_home,
                anime_id=anime['id'],
                image_url=anime['coverImage']['large'],
                title=anime['title']['userPreferred'],
                season=season,
                year=anime['startDate']['year'],
                studio=studio,
                next_airing_episode=anime['nextAiringEpisode'],
                media_format=MediaFormat[anime['format']],
                score=anime['averageScore'],
                description=anime['description'],
                genres=anime['genres']
            ))
