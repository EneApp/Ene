from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel

from ene.entities import Show
from ene.player import get_player
from ene.ui.custom import FlowLayout, EpisodeButton


class EpisodeBrowser(QWidget):
    def __init__(self, app, show: Show):
        super().__init__()
        self.current_show = show
        self.app = app

        # callbacks
        self.cleanup = None
        self.save = None
        self.refresh = None # will figure these three out later
        self.rename = None
        self.delete = None

    def register_callbacks(self, cleanup, save):
        self.cleanup = cleanup
        self.save = save

    def setup_view(self):
        menu_layout = QGridLayout()
        menu = QWidget()
        episode_widget = QWidget()
        layout = FlowLayout()
        layout.setAlignment(Qt.AlignTop)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.on_back_click)
        menu_layout.addWidget(back_button, 0, 0)

        #refresh_button = QPushButton('Refresh')
        #refresh_button.clicked.connect(self.refresh_show)
        #menu_layout.addWidget(refresh_button, 1, 0)

        #delete_button = QPushButton('Delete')
        #delete_button.clicked.connect(self.delete_show)
        #menu_layout.addWidget(delete_button, 0, 1)

        #rename_button = QPushButton('Rename')
        #rename_button.clicked.connect(self.rename_show)
        #menu_layout.addWidget(rename_button, 1, 1)

        label = QLabel(self.current_show.title)
        menu_layout.addWidget(label, 0, 2, 2, 2)
        menu.setLayout(menu_layout)
        menu.setMaximumWidth(self.width())
        menu.setMinimumWidth(self.width() / 2)

        for episode in sorted(self.current_show.episodes):
            button = EpisodeButton(episode)
            button.clicked.connect(self.play_episode)
            layout.addWidget(button)
        episode_widget.setLayout(layout)
        main_layout = QGridLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(menu, 0, 0)
        main_layout.addWidget(episode_widget, 1, 0)
        self.setLayout(main_layout)

    def on_back_click(self):
        """
        Deletes all child widgets of the layout for episodes and the layout
        itself then returns to the shows page
        """
        self.current_show = None
        layout = self.layout()
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()
        layout.deleteLater()
        self.cleanup()

    def play_episode(self):
        """
        Plays the selected episode with the users player of choice
        """
        if self.app.player is not None and self.app.player.needs_destruction():
            self.app.player = None

        if self.app.player is None:
            self.app.player = get_player(self.app.config)
        episode = self.sender().episode
        self.sender().mark_watched()
        self.save(episode)
        self.app.player.play(episode)
