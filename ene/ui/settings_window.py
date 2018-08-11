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
from PySide2.QtWidgets import (QCheckBox,
                               QComboBox,
                               QLineEdit,
                               QListView,
                               QMdiSubWindow,
                               QPushButton,
                               QStackedWidget,
                               QWidget,
                               QMessageBox)

import ene.app
from ene.constants import CONFIG_ITEM
from .window import ParentWindow

SETTINGS = {
    'Video Player': 1,
    'Local Files': 2
}


class SettingsWindow(ParentWindow, QMdiSubWindow):
    """Class for the settings window."""
    button_OK: QPushButton
    button_cancel: QPushButton
    button_apply: QPushButton
    settings_menu: QStackedWidget
    settings_list: QListView
    player: QWidget

    def __init__(self, app):
        super().__init__(app, 'settings_window.ui', 'window')
        self.current_page = self.settings_menu.currentIndex()
        self.window.setWindowTitle('Preferences')
        self._setup_children()
        self.changes = False

    def _setup_children(self):
        self.button_cancel.clicked.connect(self.window.hide)
        self.button_OK.clicked.connect(self.on_press_okay)
        self.button_apply.clicked.connect(self.save_current_page)
        self.player_type.currentIndexChanged.connect(self.pick_player)
        self.local_paths.setModel(self.populate_paths())
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

    @staticmethod
    def populate_paths():
        """
        Grabs the list of user specified paths from the config and adds them to
        the model for the path list
        """
        paths = ene.app.config.get('Local Paths')
        model = PySide2.QtGui.QStandardItemModel()
        if paths is None:
            return model
        for path in paths:
            model.appendRow(PySide2.QtGui.QStandardItem(path))
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
        """
        Saves the current page to the config file
        """
        page = self.settings_menu.widget(self.current_page)
        with ene.app.config.change() as config:
            for child in page.children():
                if child.objectName() in CONFIG_ITEM:
                    config[CONFIG_ITEM[child.objectName()]] = self.get_setting_from_child(child)
            ene.app.config.apply()
        self.changes = False

    @staticmethod
    def get_setting_from_child(child):
        """
        Gets the setting value the user has input into the child
        Args:
            child:
                The child to read a setting from
        Returns:
            The setting value
        """
        if isinstance(child, QComboBox):
            val = child.currentText()
        elif isinstance(child, QListView):
            val = None
        elif isinstance(child, QLineEdit):
            val = child.text()
        elif isinstance(child, QCheckBox):
            val = child.isChecked()
        return val

    def on_press_okay(self):
        """
        Saves the current page then exits.
        Triggered by pressing the okay button
        """
        if self.changes:
            self.save_current_page()
        self.window.hide()

    def on_changed(self):
        """
        Triggered when an item is changed in the settings
        Flags as changes made for when the user leaves the page
        """
        self.changes = True

    def pick_player(self, selection):
        """
        Hides or show player specific settings upon picking a player from the
        combo box
        Args:
            selection:
                The index of the selected item
        """
        self.on_changed()
        if selection is not 0:
            self.label_rc.hide()
            self.use_rc.hide()
        else:
            self.label_rc.show()
            self.use_rc.show()
