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

from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import QMdiSubWindow

import ene
from ene.constants import resources
from .common import load_ui_widget


# TODO: Justin implement this shit
class SettingsWindow(QMdiSubWindow):
    def __init__(self):
        super().__init__()
        with resources.path(ene.ui, 'settings.ui') as p:
            self.window = load_ui_widget(p)
        self.window.setWindowTitle('Preferences')

    def populate_settings(self):
        """
        Builds a model of settings to populate the settings menu
        :return: A Model containing the settings tree
        """
        model = QStandardItemModel()
        model.appendRow(QStandardItem('Video Player'))
        return model
