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

from PySide2.QtWidgets import QFileDialog, QMainWindow

from ene.api import MediaFormat
from ene.constants import IS_WIN
from ene.resources import Ui_window_main
from ene.util import open_source_code
from .custom import ToggleToolButton
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
        self.setupUi(self)
        self._setup_children()

    def _setup_children(self):
        """Setup all the child widgets of the main window"""
        self.action_open_folder.triggered.connect(self.choose_dir)
        self.action_source_code.triggered.connect(open_source_code)
        self.sort_toggle = ToggleToolButton(self.button_sort_order)

        # genre_future = self.app.pool.submit(self.app.api.get_genres)
        # tags_future = self.app.pool.submit(self.app.api.get_tags)
        #
        # tags = (tag['name'] for tag in tags_future.result())
        # genres = genre_future.result()
        #
        # self.genre_tag_selector = GenreTagSelector(self.combobox_genre_tag, genres, tags)
        # self.streamer_selector = StreamerSelector(self.combobox_streaming)

        self.weird = MediaDisplay(
            0,
            Path(__file__).parent /
            '..' / '..' / 'tests' / 'resource' / 'shingeki_no_kyojin_3.jpg',
            'Shingeki no Kyojin 3',
            'Wit Studio' * 10,
            {'episode': 5, 'timeUntilAiring': 320580},
            MediaFormat.TV,
            81,
            'descon ' * 200,
            ['Genre'],

        )
        self.gridlayout_season.addWidget(self.weird)

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
