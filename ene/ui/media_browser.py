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

"""This module contains the media browser"""
from pathlib import Path
from typing import List, Union

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (
    QBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from ene.api import MediaFormat
from .custom import FlexLabel


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
