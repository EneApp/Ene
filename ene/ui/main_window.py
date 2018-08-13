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

from ene.constants import APP_NAME, IS_WIN
from ene.util import open_source_code
from .custom import AnimeDisplay, GenreTagSelector, StreamerSelector, ToggleToolButton
from .window import ParentWindow


class MainWindow(ParentWindow, QMainWindow):
    """
    Main form of the application
    """

    def __init__(self, app):
        """
        Initialize the ui files for the application
        """
        super().__init__(app, 'main_window.ui', 'window')
        self.window.setWindowTitle(APP_NAME)
        self.setWindowTitle(APP_NAME)
        self._setup_children()

    def _setup_children(self):
        """Setup all the child widgets of the main window"""
        self.action_open_folder.triggered.connect(self.choose_dir)
        self.action_source_code.triggered.connect(open_source_code)
        self.sort_toggle = ToggleToolButton(self.button_sort_order)

        genre_future = self.app.pool.submit(self.app.api.get_genres)
        tags_future = self.app.pool.submit(self.app.api.get_tags)

        tags = (tag['name'] for tag in tags_future.result())
        genres = genre_future.result()

        self.genre_tag_selector = GenreTagSelector(self.combobox_genre_tag, genres, tags)
        self.streamer_selector = StreamerSelector(self.combobox_streaming)

        self.weird = AnimeDisplay(
            0,
            Path(__file__).parent
            / '..' / '..' / 'tests' / 'resource' / 'shingeki_no_kyojin_3.jpg',
            'Shingeki no Kyojin 3',
            'Wit Studio',
            parent=self.widget_tab
        )
        self.weird.move(200, 50)

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
