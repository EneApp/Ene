from pathlib import Path

from PySide2.QtWidgets import QWidget, QLineEdit, QMessageBox, QPushButton, QStackedWidget, QFileDialog
from PySide2.QtCore import Qt

from ene.constants import IS_WIN
from ene.series_manager import SeriesManager
from ene.ui.custom import FlowLayout, SeriesButton
from ene.ui.widgets.episode_browser import EpisodeBrowser


class SeriesBrowser(QWidget):
    def __init__(self, app, series: SeriesManager, stack_local_files: QStackedWidget):
        super().__init__()
        self.search = None
        self.current_show = None
        self.episode_browser = None
        self.series = series
        self.stack_local_files = stack_local_files
        self.app = app

    def init_layout(self):
        series_layout = FlowLayout()
        series_layout.setContentsMargins(11, 75, 11, 11)
        series_layout.setAlignment(Qt.AlignTop)
        series_layout.setSizeConstraint(FlowLayout.SetMaximumSize)
        self.setLayout(series_layout)

    def setup_search(self, parent_page):
        """
        Sets up the search area
        """
        self.search = QWidget()
        search_bar = QLineEdit()
        search_bar.setParent(self.search)
        search_bar.setGeometry(11, 11, self.width(), 35)
        search_bar.setPlaceholderText("Search...")
        search_button = QPushButton()
        search_button.setParent(self.search)
        search_button.setGeometry(self.width() + 15, 11, 150, 35)
        search_button.setText("Search")
        #search_button.clicked.connect(parent_page)
        self.search.setParent(parent_page)

    def refresh_shows_view(self):
        """
        Refreshes the local files UI, updating any existing series buttons and creating
        any new ones
        """
        for show in sorted(self.series.get_all_shows()):
            existing = self.findChild(SeriesButton, show.title)
            if not existing:
                button = SeriesButton(show)
                button.clicked.connect(self.on_series_click)
                button.add_action('Delete', self.delete_show_action)
                button.add_action('Organize', self.organize)
                button.add_action('Fetch Cover from AniList', self.fetch_cover)
                button.add_action('Set Cover Image from saved file', self.set_cover)
                self.layout().addWidget(button)
            else:
                existing.update_episode_count(len(show))

    def on_series_click(self, *, show=None):
        """
        Sets up the window for the episodes of a show. Triggered when a show is
        clicked from the local files page
        """
        if show is None:
            show = self.sender().title
        current_show = self.series.get_show(show)
        self.episode_browser = EpisodeBrowser(self.app, current_show)
        self.episode_browser.width = self.width
        self.episode_browser.height = self.height
        self.episode_browser.register_callbacks(self.cleanup_episode_view, self.series.save_episode)
        self.episode_browser.setup_view()
        self.stack_local_files.addWidget(self.episode_browser)
        self.stack_local_files.setCurrentIndex(1)

    def cleanup_episode_view(self):
        self.stack_local_files.setCurrentIndex(0)
        self.stack_local_files.removeWidget(self.episode_browser)
        self.episode_browser = None

    def delete_show_action(self):
        """
        Deletes a single show using right click > Delete on a show
        """
        prompt = QMessageBox.question(self, 'Delete', 'Delete files on disk as well?',
                                      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        print(prompt)
        if prompt != QMessageBox.Cancel:
            self.sender().parentWidget().deleteLater()
            self.series.delete_show(self.sender().parentWidget().title, prompt == QMessageBox.Yes)

    def organize(self):
        """
        Organizes a single show using right click > Organize on a show
        """
        self.series.organize_show(self.sender().parentWidget().title)

    def fetch_cover(self):
        res = self.app.api.get_show(self.sender().parentWidget().title)
        if res.is_ok:
            media = res.unwrap()
            image = media.cover_image.unwrap()
            self.series.set_cover_art(self.sender().parentWidget().title, image)
            self.sender().parentWidget().set_image(image)
        else:
            print('bad response')
            print(res.unwrap_err())

    def set_cover(self):
        path = self.choose_file()
        if path:
            self.series.set_cover_art(self.sender().parentWidget().title, path)
            self.sender().parentWidget().set_image(path)

    def choose_file(self) -> Path:
        """
        Choose a file from a file dialog

        Returns: A Path object with the selected file
        """
        args = [self, self.tr("Open Directory"), str(Path.home())]
        if IS_WIN:
            args.append(QFileDialog.DontUseNativeDialog)
        dir_ = QFileDialog.getOpenFileName(*args)
        return Path(dir_[0])
