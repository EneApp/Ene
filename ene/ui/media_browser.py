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
from typing import List, Optional, Union

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ene.api import MediaFormat, MediaSeason
from .common import mk_padding, mk_stylesheet


class MediaDisplay(QWidget):
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

    def __init__(
            self,
            anime_id: int,
            image_path: Union[Path, str],
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
        # TODO: Refactor this shit
        super().__init__(*args, **kwargs)
        self.setFixedWidth(self.image_w * 2)
        self.setFixedHeight(self.image_h)

        self.anime_id = anime_id
        self.season = season
        self.year = year
        self.next_airing_episode = next_airing_episode
        self.media_format = media_format
        self.score = score
        self.description = description
        self.genres = genres

        self._setup_layouts()
        self._setup_left(
            (QPixmap(str(image_path)).scaled(self.image_w, self.image_h, Qt.KeepAspectRatio)),
            title,
            studio
        )
        self._setup_airing()
        self._setup_format()
        self._setup_des()

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
        self.left_label = QLabel()
        self.left_label.setPixmap(image)
        stylesheet = {
            'color': self.lighter_white,
            'background-color': self.transparent_grey,
            'padding': '10px',
            'font-size': '14pt',
            'qproperty-wordWrap': 'true',
            'qproperty-alignment': '"AlignVCenter | AlignLeft"',
        }

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))

        if studio:
            self.studio_label = QLabel(studio)
            stylesheet['color'] = self.aqua
            stylesheet['padding'] = mk_padding(0, 10, 10, 10)
            stylesheet['font-size'] = '12pt'
            self.studio_label.setStyleSheet(mk_stylesheet(stylesheet, 'QLabel'))
        else:
            self.studio_label = None

        for lbl in filter(None, (self.title_label, self.studio_label)):
            lbl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.left_label.setLayout(self.left_layout)

        self.master_layout.addWidget(self.left_label)
        self.master_layout.addLayout(self.right_layout)

        self.left_layout.addWidget(self.title_label)
        if self.studio_label:
            self.left_layout.addWidget(self.studio_label)

    def _setup_airing(self):
        next_airing_episode = self.next_airing_episode or {}
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

            self.next_airing_label = QLabel(f'Ep {next_episode} - {time_str}')
        else:
            self.next_airing_label = QLabel(f'{self.season.name.title()} {self.year}')
        self.next_airing_label.setStyleSheet(mk_stylesheet(
            {
                'color': self.aqua,
                'background-color': self.dark_grey,
                'padding': '5px',
                'font-size': '11pt',
                'qproperty-alignment': '"AlignCenter"'
            },
            'QLabel'
        ))
        self.right_layout.addWidget(self.next_airing_label)
        self.right_layout.addLayout(self.right_mid_layout)

    def _setup_format(self):
        self.format_label = QLabel(self.media_format.name)
        self.format_label.setStyleSheet(mk_stylesheet(
            {
                'color': self.dark_white,
                'background-color': self.grey,
                'padding': '5px',
                'font-size': '11pt',
                'qproperty-alignment': '"AlignCenter"'
            },
            'QLabel'
        ))
        self.right_mid_layout.addWidget(self.format_label)

        if self.score is None:
            self.score_label = None
        else:
            self.score_label = QLabel(f'{self.score}%')
            self.score_label.setStyleSheet(mk_stylesheet(
                {
                    'color': self.dark_white,
                    'background-color': self.grey,
                    'padding': '5px',
                    'font-size': '11pt',
                    'qproperty-alignment': '"AlignCenter"'
                },
                'QLabel'
            ))
            self.right_mid_layout.addWidget(self.score_label)

    def _setup_des(self):
        self.desc_label = QLabel(self.description)
        self.desc_label.setStyleSheet(mk_stylesheet(
            {
                'color': self.dark_white,
                'background-color': self.light_grey,
                'padding': '5px',
                'font-size': '10pt',
                'qproperty-alignment': '"AlignLeft"',
                'qproperty-wordWrap': 'true'
            },
            'QLabel'
        ))
        self.desc_scroll = QScrollArea()
        self.desc_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.desc_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.desc_scroll.setWidgetResizable(True)
        self.desc_scroll.setStyleSheet(mk_stylesheet({'border': 'none'}, 'QScrollArea'))
        self.desc_scroll.setWidget(self.desc_label)

        self.right_layout.addWidget(self.desc_scroll)

    def _setup_bottom_bar(self):
        # TODO Need to show buttons on hover
        self.genre_label = QLabel(', '.join(self.genres))
        self.genre_label.setStyleSheet(mk_stylesheet(
            {
                'color': self.dark_white,
                'background-color': self.grey,
                'padding': '5px',
                'qproperty-wordWrap': 'true'
            },
            'QLabel'
        ))
        self.genre_label.setAlignment(Qt.AlignCenter)

        self.bottom_right_layout.addWidget(self.genre_label)
        self.right_layout.addWidget(self.genre_label)
