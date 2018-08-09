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
from PySide2.QtWidgets import QMdiSubWindow, QMessageBox

from .window import ParentWindow

SETTINGS = {
    'Video Player': 1,
    'Local Files': 2
}


# TODO: Justin finish implementing this
class SettingsWindow(ParentWindow, QMdiSubWindow):
    """Class for the settings window."""

    def __init__(self, app):
        super().__init__(app, 'settings_window.ui', 'window')
        self.current_page = self.settings_menu.currentIndex()
        self.window.setWindowTitle('Preferences')
        self._setup_children()
        self.changes = False

    def _setup_children(self):
        self.button_cancel.clicked.connect(self.window.hide)
        self.button_OK.clicked.connect(self.on_press_okay())
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
        if self.changes:
            save = QMessageBox.question(self.window,
                                        "Save",
                                        "Changes detected. Save current page?")
            if save == QMessageBox.Yes:
                self.save_current_page()
        # reset the page
        index = selected.indexes()[0].data()
        self.settings_menu.setCurrentIndex(SETTINGS[index])
        self.current_page = SETTINGS[index]
        self.changes = False

    def save_current_page(self):
        page = self.settings_menu.childAt(self.current_page, 0)

    def on_press_okay(self):
        self.save_current_page()
        self.window.hide()
