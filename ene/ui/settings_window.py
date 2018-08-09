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

"""This module contains the settings window."""
import PySide2.QtGui
from PySide2.QtWidgets import QListView, QMdiSubWindow, QPushButton, QStackedWidget

from .window import ParentWindow

SETTINGS = {
    'Video Player': 1,
    'AniList': 2
}


# TODO: Justin finish implementing this
class SettingsWindow(ParentWindow, QMdiSubWindow):
    """Class for the settings window."""
    button_OK: QPushButton
    button_cancel: QPushButton
    settings_menu: QStackedWidget
    settings_list: QListView

    def __init__(self, app):
        children = {
            'window': [
                'button_OK',
                'button_cancel',
                'settings_menu',
                'settings_list',
            ],
        }
        super().__init__(app, 'settings_window.ui', children)
        self.window.setWindowTitle('Preferences')

    def _setup_children(self, children):
        super()._setup_children(children)
        self.button_cancel.clicked.connect(self.window.hide)
        model = self.populate_settings()
        self.settings_list.setModel(model)
        self.settings_list.selectionModel().selectionChanged.connect(self.on_select_setting)

    @staticmethod
    def populate_settings():
        """
        Builds a model of settings items from the dictionary
        Returns:
            The item model for all settings
        """
        model = PySide2.QtGui.QStandardItemModel()
        for setting in SETTINGS:
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
