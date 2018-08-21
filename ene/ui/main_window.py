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

"""This module contains the main window."""
from pathlib import Path

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFileDialog, QGridLayout, QHBoxLayout, QLabel, QLayout, QMainWindow,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from ene.api import MediaFormat, MediaSeason
from ene.constants import IS_WIN
from ene.resources import Ui_window_main
from ene.util import open_source_code
from .custom import FlowLayout, GenreTagSelector, StreamerSelector, ToggleToolButton
from .media_browser import MediaDisplay


class MainWindow(QMainWindow, Ui_window_main):
    """
    Main form of the application
    """

    def __init__(self, app):
        """
        Initialize the ui files for the application
        """
        super().__init__()
        self.app = app
        # self.files = FileManager(ene.app.config)
        self.setupUi(self)
        self._setup_children()

    def _setup_children(self):
        """Setup all the child widgets of the main window"""
        self._setup_tab_browser()
        self.action_open_folder.triggered.connect(self.choose_dir)
        self.action_source_code.triggered.connect(open_source_code)
        # self._setup_tab_files()

    def _setup_tab_browser(self):
        master_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = FlowLayout(None, 10, 10, 10)
        left_mid_top_layout = QHBoxLayout()
        left_mid_bot_layout = QHBoxLayout()

        left_layout.setAlignment(Qt.AlignTop)

        left_layout_control = QWidget()
        left_layout_control.setLayout(left_layout)
        right_layout_control = QWidget()
        right_layout_control.setLayout(right_layout)
        self.tab_browser.setLayout(master_layout)
        # genre_future = self.app.pool.submit(self.app.api.get_genres)
        # tags_future = self.app.pool.submit(self.app.api.get_tags)

        # tags = [tag['name'] for tag in tags_future.result()]
        # genres = genre_future.result()
        tags = ['']
        genres = ['']

        left_layout.addWidget(self.label_season)
        left_layout.addWidget(self.combobox_season)
        left_mid_top_layout.addWidget(self.label_year)
        left_mid_top_layout.addWidget(self.label_year_number)
        left_layout.addLayout(left_mid_top_layout)
        left_layout.addWidget(self.slider_year)
        left_layout.addWidget(self.label_filter)
        left_mid_bot_layout.addWidget(self.combobox_sort)
        left_mid_bot_layout.addWidget(self.button_sort_order)
        left_layout.addLayout(left_mid_bot_layout)
        left_layout.addWidget(self.combobox_format)
        left_layout.addWidget(self.combobox_status)
        left_layout.addWidget(self.combobox_streaming)
        left_layout.addWidget(self.combobox_genre_tag)
        self.genre_tag_selector = GenreTagSelector(self.combobox_genre_tag, genres, tags)
        self.streamer_selector = StreamerSelector(self.combobox_streaming)
        self.sort_toggle = ToggleToolButton(self.button_sort_order)

        self.weirds = [
            MediaDisplay(
                i,
                Path(__file__).parent /
                '..' / '..' / 'tests' / 'resource' / 'shingeki_no_kyojin_3.jpg',
                'Shingeki no Kyojin 3' * 3,
                MediaSeason.SUMMER,
                2018,
                'Wit Studio' * 10,
                {'episode': 5, 'timeUntilAiring': 320580},
                MediaFormat.TV,
                81,
                'descon ' * 200,
                ['Genre'],
            ) for i in range(20)
        ]

        self.weird_scroll = QScrollArea()
        self.weird_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.weird_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.weird_scroll.setWidget(right_layout_control)
        self.weird_scroll.setWidgetResizable(True)

        left_layout_control.setMaximumWidth(self.slider_year.width())
        master_layout.addWidget(left_layout_control)
        master_layout.addWidget(self.weird_scroll)
        right_layout.setSizeConstraint(QLayout.SetMinimumSize)
        for i, weird in enumerate(self.weirds):
            right_layout.addWidget(weird)
        left_layout.setSpacing(0)
        left_layout.setMargin(0)

    def _setup_tab_files(self):
        """
        Sets up the local files tab. Triggered when the tab is selected
        """
        self.files.build_shows_from_db()
        layout = QGridLayout()

        for i, show in enumerate(self.files.series):
            button = QPushButton(show)
            button.clicked.connect(self.on_series_click)
            layout.addWidget(button, i / 3, i % 3)

        self.stack_local_files.currentWidget().setLayout(layout)

    def on_series_click(self):
        """
        Sets up the window for the episodes of a show. Triggered when a show is
        clicked from the local files page
        """
        self.stack_local_files.setCurrentIndex(1)
        layout = QGridLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.on_back_click)
        layout.addWidget(back_button, 0, 0)
        label = QLabel(self.sender().text())
        layout.addWidget(label, 0, 1, 1, 2)
        self.files.fetch_db_episodes_for_show(self.sender().text())
        episodes = self.files.get_readable_names(self.sender().text())
        for i, episode in enumerate(episodes):
            button = QPushButton(episode)
            layout.addWidget(button, (i / 3) + 1, i % 3)
        self.stack_local_files.currentWidget().setLayout(layout)

    def on_back_click(self):
        """
        Deletes all child widgets of the layout for episodes and the layout
        itself then returns to the shows page
        """
        layout = self.stack_local_files.currentWidget().layout()
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        layout.deleteLater()
        self.stack_local_files.setCurrentIndex(0)

    def choose_dir(self) -> Path:
        """
        Choose a directory from a file dialog

        Returns: The directory path
        """
        args = [self, self.tr("Open Directory"), str(Path.home())]
        if IS_WIN:
            args.append(QFileDialog.DontUseNativeDialog)
        dir_ = QFileDialog.getExistingDirectory(*args)
        # TODO do something with this
        return Path(dir_)
