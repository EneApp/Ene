#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2020 Peijun Ma, Justin Sedge
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
from enum import Enum
from pathlib import Path

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ene.constants import IS_WIN
from ene.resources import Ui_window_main
from ene.series_manager import SeriesManager
from ene.util import open_source_code
from ene.ui.widgets.media_browser import MediaBrowser
from ene.ui.widgets.series_browser import SeriesBrowser
from .custom import EpisodeButton, SeriesButton


class MainWindow(QMainWindow, Ui_window_main):
    """Main window of the application."""

    class Tabs(Enum):
        Files = 0
        Streams = 1
        Browse = 2
        MyList = 3

    def __init__(self, app):
        """
        Initialize the ui files for the application
        """
        super().__init__()
        self.app = app
        #  TODO: These three lines should be moved somewhere else
        self.series = SeriesManager(self.app.config)
        self.series.init_db(self.app.data_home)
        self.series.fetch_shows_from_db()

        self.player = None
        self.current_show = None
        self.setupUi(self)

    def setupUi(self, window_main):
        """Setup all the child widgets of the main window"""
        super().setupUi(window_main)
        self._setup_tab_browser()
        self._setup_tab_files()
        self.action_open_folder.triggered.connect(self.choose_dir)
        self.action_source_code.triggered.connect(open_source_code)
        self.action_refresh_library.triggered.connect(self.refresh_library)
        self.widget_tab.currentChanged.connect(self.handle_current_tab_changed)

    @Slot(int)
    def handle_current_tab_changed(self, index):
        """
        Handles when the tab changes in the widget tab.

        Args:
            index:
                The index of the new tab

        Returns:
            None
        """
        if index == self.Tabs.Browse:
            if not self.media_browser.is_setup:
                self.media_browser.is_setup = True
                self.app.pool.submit(
                    self.media_browser.fetch_control_info,
                    self.combobox_genre_tag,
                    self.combobox_streaming,
                )
            self.check_box_adult.setVisible(self.app.config.get(
                'Allow Adult Content',
                default=False))

    def _setup_tab_browser(self):
        self.media_browser = MediaBrowser(
            self.app,
            self.button_sort_order,
            self.combobox_season,
            self.spinbox_year_min,
            self.spinbox_year_max,
            self.combobox_sort,
            self.combobox_format,
            self.combobox_status,
            self.check_box_on_list,
            self.check_box_adult
        )

        master_layout = QHBoxLayout()
        self.tab_browser.setLayout(master_layout)

        left_mid_bot_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)

        left_layout_control = QWidget()
        left_layout_control.setLayout(left_layout)

        left_layout.addWidget(self.label_season)
        left_layout.addWidget(self.combobox_season)
        left_layout.addWidget(self.groupbox_year)
        left_layout.addWidget(self.label_filter)
        left_mid_bot_layout.addWidget(self.combobox_sort)
        left_mid_bot_layout.addWidget(self.button_sort_order)
        left_layout.addLayout(left_mid_bot_layout)
        left_layout.addWidget(self.combobox_format)
        left_layout.addWidget(self.combobox_status)
        left_layout.addWidget(self.combobox_streaming)
        left_layout.addWidget(self.combobox_genre_tag)
        left_layout.addWidget(self.check_box_on_list)
        left_layout.addWidget(self.check_box_adult)

        left_layout_control.setMaximumWidth(self.groupbox_year.width())
        left_layout.setSpacing(0)
        left_layout.setMargin(0)

        master_layout.addWidget(left_layout_control)
        master_layout.addWidget(self.media_browser)

    def _setup_tab_files(self):
        """
        Sets up the local files tab. Triggered when the tab is selected
        """

        self.page_widget = SeriesBrowser(self.app, self.series, self.stack_local_files)
        self.page_widget.init_layout()
        series_page = QScrollArea()
        series_page.setWidget(self.page_widget)
        series_page.setWidgetResizable(True)
        self.page_widget.setup_search(series_page)
        self.stack_local_files.addWidget(series_page)
        self.page_widget.refresh_shows_view()

    def refresh_show(self):
        """
        Refreshes the episodes for the current show and dumps the new shows to
        the database. Triggered by clicking Refresh in the view for a show
        """
        new = self.files.refresh_single_show(self.current_show)
        layout = self.stack_local_files.currentWidget().layout()
        for episode in new:
            button = EpisodeButton(episode)
            button.clicked.connect(self.play_episode)
            layout.addWidget(button)
        self.files.dump_to_db()

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

    def refresh_library(self):
        """
        Triggers a full refresh of the users library, updating episode counts
        and adding new shows to the UI as needed
        """
        self.series.fetch_shows_from_files()
        self.series.save_shows()
        self.page_widget.refresh_shows_view()

    def rename_show(self):
        """
        Renames the current show. Displays an input box to get the new name
        """
        title = QInputDialog().getText(self,
                                       'Rename',
                                       'New Title:',
                                       text=self.current_show)
        if title[1]:
            self.series.rename_show(self.current_show, title[0])

    def delete_show(self):
        """
        Deletes the current show
        """
        self.series.delete_show(self.current_show)
        self.on_back_click()

    def search_shows(self):
        """
        Hides all shows that do not match the search criteria
        """
        search_text = self.search.findChild(QLineEdit).text().lower()
        # TODO: Make this not break the FlowLayout
        for show in self.page_widget.findChildren(SeriesButton):
            if search_text not in show.title.lower():
                show.hide()
            else:
                show.show()
        self.page_widget.layout().do_layout(self.page_widget.rect(), False)
