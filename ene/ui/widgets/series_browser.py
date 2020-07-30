from PySide2.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QGridLayout, QStackedWidget, QScrollArea
from PySide2.QtCore import Qt

from ene.series_manager import SeriesManager
from ene.ui.custom import FlowLayout, SeriesButton, EpisodeButton
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
        for show, num_episodes in sorted(self.series.get_shows_overview()):
            existing = self.findChild(SeriesButton, show)
            if not existing:
                button = SeriesButton(show, num_episodes)
                button.clicked.connect(self.on_series_click)
                button.add_action('Delete', self.delete_show_action)
                self.layout().addWidget(button)
            else:
                existing.update_episode_count(num_episodes)

    def on_series_click(self, *, show=None):
        """
        Sets up the window for the episodes of a show. Triggered when a show is
        clicked from the local files page
        """
        if show is None:
            show = self.sender().title
        current_show = self.series.get_show(show)
        self.episode_browser = EpisodeBrowser(self.app, current_show)
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
        self.sender().parentWidget().deleteLater()
        self.series.delete_show(self.sender().parentWidget().title)
