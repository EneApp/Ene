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

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import ene.player
from ene.constants import IS_WIN
from ene.files import FileManager
from ene.resources import Ui_window_main
from ene.util import open_source_code
from .custom import EpisodeButton, FlowLayout, SeriesButton
from .media_browser import MediaBrowser


class MainWindow(QMainWindow, Ui_window_main):
    """Main window of the application."""

    def __init__(self, app):
        """
        Initialize the ui files for the application
        """
        super().__init__()
        self.app = app
        self.files = FileManager(self.app.config, self.app.data_home)
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
        if index == 2:
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
        # TODO: Refactor
        self.files.build_all_from_db()
        series_layout = FlowLayout()
        series_layout.setContentsMargins(11, 75, 11, 11)
        series_layout.setAlignment(Qt.AlignTop)

        for show in sorted(self.files.series):
            button = SeriesButton(show, len(self.files.series[show]))
            button.clicked.connect(self.on_series_click)
            button.add_action('Delete', self.delete_show_action)
            series_layout.addWidget(button)

        series_layout.setSizeConstraint(FlowLayout.SetMaximumSize)
        self.page_widget = QWidget()
        self.page_widget.setLayout(series_layout)
        series_page = QScrollArea()
        series_page.setWidget(self.page_widget)
        series_page.setWidgetResizable(True)
        self._setup_search()
        self.search.setParent(series_page)
        self.stack_local_files.addWidget(series_page)
        self.stack_local_files.addWidget(QWidget())

    def _setup_search(self):
        """
        Sets up the search area
        """
        self.search = QWidget()
        search_bar = QLineEdit()
        search_bar.setParent(self.search)
        search_bar.setGeometry(11, 11, self.page_widget.width(), 35)
        search_bar.setPlaceholderText("Search...")
        search_button = QPushButton()
        search_button.setParent(self.search)
        search_button.setGeometry(self.page_widget.width() + 15, 11, 150, 35)
        search_button.setText("Search")
        search_button.clicked.connect(self.search_shows)

    def on_series_click(self, *, show=None):
        """
        Sets up the window for the episodes of a show. Triggered when a show is
        clicked from the local files page
        """
        if show is None:
            show = self.sender().title
        self.current_show = show
        self.stack_local_files.setCurrentIndex(1)
        menu_layout = QGridLayout()
        menu = QWidget()
        layout = FlowLayout()
        layout.setAlignment(Qt.AlignTop)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.on_back_click)
        menu_layout.addWidget(back_button, 0, 0)

        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.refresh_show)
        menu_layout.addWidget(refresh_button, 1, 0)

        delete_button = QPushButton('Delete')
        delete_button.clicked.connect(self.delete_show)
        menu_layout.addWidget(delete_button, 0, 1)

        rename_button = QPushButton('Rename')
        rename_button.clicked.connect(self.rename_show)
        menu_layout.addWidget(rename_button, 1, 1)

        label = QLabel(show)
        menu_layout.addWidget(label, 0, 2, 2, 2)
        menu.setLayout(menu_layout)
        menu.setMaximumWidth(self.stack_local_files.width())
        menu.setMinimumWidth(self.stack_local_files.width() / 2)
        layout.addWidget(menu)

        self.files.series[show].sort()
        for episode in self.files.series[show]:
            button = EpisodeButton(episode)
            button.clicked.connect(self.play_episode)
            layout.addWidget(button)
        self.stack_local_files.currentWidget().setLayout(layout)

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

    def play_episode(self):
        """
        Plays the selected episode with the users player of choice
        """
        if self.player is not None and self.player.needs_destruction():
            self.player = None

        if self.player is None:
            self.player = ene.player.get_player(self.app.config)
        episode = self.sender().path
        self.player.play(str(episode))

    def on_back_click(self):
        """
        Deletes all child widgets of the layout for episodes and the layout
        itself then returns to the shows page
        """
        self.current_show = None
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

    def refresh_library(self):
        """
        Triggers a full refresh of the users library, updating episode counts
        and adding new shows to the UI as needed
        """
        old = set(self.files.series.keys())
        self.files.refresh_shows()
        new = set(self.files.series.keys()) - old
        for show in self.page_widget.children():
            if isinstance(show, SeriesButton):
                show.update_episode_count(len(self.files.series[show.title]))
        for show in sorted(new):
            button = SeriesButton(show, len(self.files.series[show]))
            button.clicked.connect(self.on_series_click)
            self.page_widget.layout().addWidget(button)
        self.files.dump_to_db()

    def rename_show(self):
        """
        Renames the current show. Displays an input box to get the new name
        """
        title = QInputDialog().getText(self,
                                       'Rename',
                                       'New Title:',
                                       text=self.current_show)
        if title[1]:
            self.files.rename_show(self.current_show, title[0])

    def delete_show(self):
        """
        Deletes the current show
        """
        self.files.delete_show(self.current_show)
        self.on_back_click()

    def delete_show_action(self):
        """
        Deletes a single show using right click > Delete on a show
        """
        self.sender().parentWidget().deleteLater()
        self.files.delete_show(self.sender().parentWidget().title)

    def search_shows(self):
        """
        Hides all shows that do not match the search criteria
        """
        search_text = self.search.findChild(QLineEdit).text().lower()
        print(search_text)
        # TODO: Make this not break the FlowLayout
        for show in self.page_widget.findChildren(SeriesButton):
            if search_text not in show.title.lower():
                show.hide()
            else:
                show.show()
        self.page_widget.layout().do_layout(self.page_widget.rect(), False)
