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
        self.player_type.currentIndexChanged.connect(self.pick_player)
        self.reset_page()
        self.setup_listeners()
        self.button_cancel.clicked.connect(self.window.hide)
        self.button_OK.clicked.connect(self.on_press_okay)
        self.button_apply.clicked.connect(self.save_current_page)
        self.button_apply.setEnabled(False)
        path_model = self.populate_paths()
        path_model.itemChanged.connect(self.on_changed)
        self.local_paths.setModel(path_model)
        model = self.populate_settings()
        self.settings_list.setModel(model)
        self.settings_list.selectionModel().selectionChanged.connect(self.on_select_setting)

    def setup_listeners(self):
        """
        Sets up listeners for children to trigger events
        """
        page = self.settings_menu.widget(self.current_page)
        for child in page.children():
            if child.objectName() in CONFIG_ITEM:
                self.attach_change_listener(child)

    def attach_change_listener(self, child):
        """
        Connects on_changed to a child's signal, the signal is based on the
        type of the child
        Args:
            child:
                The child to connect the listener to
        """
        if isinstance(child, QComboBox):
            child.currentIndexChanged.connect(self.on_changed)
        elif isinstance(child, QLineEdit):
            child.textEdited.connect(self.on_changed)
        elif isinstance(child, QCheckBox):
            child.stateChanged.connect(self.on_changed)

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
        self.reset_page()
        index = selected.indexes()[0].data()
        self.settings_menu.setCurrentIndex(SETTINGS[index])
        self.current_page = SETTINGS[index]
        self.changes = False
        self.button_apply.setEnabled(False)

    def reset_page(self):
        """
        Resets settings items on the page to the value in the config
        """
        page = self.settings_menu.widget(self.current_page)
        for child in page.children():
            if child.objectName() in CONFIG_ITEM:
                setting = ene.app.config.get(CONFIG_ITEM[child.objectName()])
                if setting is None:
                    continue
                self.set_setting_for_child(child, setting)

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
        self.button_apply.setEnabled(False)

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
        else:
            raise NotImplementedError
        return val

    @staticmethod
    def set_setting_for_child(child, setting):
        """
        Populates a child with the setting value from the config
        Args:
            child:
                The child to modify
            setting:
                The saved setting value
        """
        if isinstance(child, QComboBox):
            child.setCurrentText(setting)
        elif isinstance(child, QLineEdit):
            child.setText(setting)
        elif isinstance(child, QCheckBox):
            child.setChecked(setting)

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
        self.button_apply.setEnabled(True)

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
