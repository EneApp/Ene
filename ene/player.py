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

import sys
from abc import ABCMeta, abstractmethod

import vlc
from PySide2.QtWidgets import QFrame


class Player(metaclass=ABCMeta):
    """
    Abstract base class for video player
    """

    @abstractmethod
    def add(self, path):
        """
        Add a file to the play list

        Args:
            path: Path to the file to add
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def title(self) -> str:
        """
        Get the title of the currently playing video
        Returns:
            The title of the video
        """
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        """
        Setop the player
        """
        raise NotImplementedError()


class VLCPlayer(Player):
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def play(self):
        if sys.platform == "darwin":
            self.vlcWidget = QFrame()
            self.vlcWidget.resize(700, 700)
            self.vlcWidget.show()
            self.player.set_nsobject(self.vlcWidget.winId())

        self.player.play()

    def add(self, path):
        self.media = self.instance.media_new(path)
        self.player.set_media(self.media)

    @property
    def title(self):
        return self.player.title

    def stop(self):
        self.player.stop()
