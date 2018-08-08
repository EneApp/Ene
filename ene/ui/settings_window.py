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

import PySide2.QtGui
from PySide2.QtWidgets import QListView, QMdiSubWindow, QPushButton, QStackedWidget

import ene
from ene.constants import resources
from .common import ChildFinderMixin, load_ui_widget

SETTINGS = {
    'Video Player': 1,
    'AniList': 2
}


# TODO: Justin finish implementing this
class SettingsWindow(QMdiSubWindow, ChildFinderMixin):
    button_OK: QPushButton
    button_cancel: QPushButton
    settings_menu: QStackedWidget
    settings_list: QListView

    def __init__(self):
        super().__init__()
        with resources.path(ene.ui, 'settings_window.ui') as p:
            self.window = load_ui_widget(p)
        self.window.setWindowTitle('Preferences')
        self._setup_children({
            'window': [
                'button_OK',
                'button_cancel',
                'settings_menu',
                'settings_list'
            ]
        })

    def _setup_children(self, children):
        super()._setup_children(children)
        self.button_cancel.clicked.connect(self.window.hide)
        model = self.populate_settings()
        self.settings_list.setModel(model)
        self.settings_list.selectionModel().selectionChanged.connect(self.on_select_setting)

    def populate_settings(self):
        """
        Builds a model of settings items from the dictionary
        Returns:
            The item model for all settings
        """
        model = PySide2.QtGui.QStandardItemModel()
        for setting in SETTINGS.keys():
            model.appendRow(PySide2.QtGui.QStandardItem(setting))

        return model

    def on_select_setting(self, selected):
        """
        Triggered when a new settings item is selected from the list. Updates
        the stacked widget to the appropriate page for the selected item
        Args:
            selected:
                The selected item
        """
        index = selected.indexes()[0].data()
        self.settings_menu.setCurrentIndex(SETTINGS[index])
