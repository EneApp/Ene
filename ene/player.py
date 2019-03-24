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

"""This module handles video playback on different players."""

import subprocess
from abc import ABC, abstractmethod
from shutil import which
from threading import Event
from time import sleep
import requests

from ene.persistence.models import Episode


from ene.constants import IS_MAC, IS_WIN


class AbstractPlayer(ABC):
    """Base media player class."""

    @abstractmethod
    def play(self, episode: Episode):
        """
        Plays the media file given by path

        Args:
            episode: The location of the media file to play
        """
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        """Stop playing."""
        raise NotImplementedError()

    @abstractmethod
    def wait_for_playback_end(self):
        """Wait for the playback to end."""
        raise NotImplementedError()

    @abstractmethod
    def needs_destruction(self):
        """Should the instance be destroyed"""
        raise NotImplementedError()


class VlcPlayer(AbstractPlayer):
    """
    An implementation of the VLC player using the python-vlc library
    """

    def __init__(self):
        import vlc
        self.instance = vlc.Instance('--extraintf=hotkeys')
        self.player = self.instance.media_player_new()
        self.player.video_set_key_input(True)
        self.player.video_set_mouse_input(True)

    def play(self, episode: Episode):
        """
        Play the media file using vlc by the given path.
        Args:
            episode: Path to the media file
        """
        media = self.instance.media_new(episode.path)
        self.player.set_media(media)
        self.player.play()

    def stop(self):
        self.player.stop()

    def wait_for_playback_end(self):
        sleep(30)

    def needs_destruction(self):
        return False


class HttpVlcPlayer(AbstractPlayer):
    """An implementation of the Vlc player using HTTP requests"""

    # The HTTP interface requires a password so its gonna be ene for now
    PASSWORD = 'ene'

    def __init__(self, ip, binary=None):
        if not binary and IS_WIN:
            binary = which('vlc.exe')
        elif not binary:
            binary = which('vlc')

        args = [binary, '-I']
        if IS_MAC:
            # mac is special
            args.append('macosx')
        else:
            args.append('qt')
        args.append('--extraintf=http')
        args.append('--http-password=' + self.PASSWORD)

        self.base = f'http://:{self.PASSWORD}@{ip}/requests/'
        self.process = subprocess.Popen(args)
        sleep(1)

    def play(self, episode: Episode):
        url = f'{self.base}status.json?command=in_play&input={episode.path}'
        requests.get(url)

    def stop(self):
        requests.get(f'{self.base}?command=pl_empty')

    def wait_for_playback_end(self):
        pass

    def needs_destruction(self):
        try:
            # if a request gives a non 200 status code just destroy it
            res = requests.get(f'{self.base}status.json')
            return res.status_code != 200
        except requests.exceptions.ConnectionError:
            # more likely is a connection failure. destroy it in this case
            return True


class MpvPlayer(AbstractPlayer):
    """
    An implementation of the MPV player using the python-mpv library
    """

    def __init__(self):
        """
        Sets up a new MPV instance with the default keybindings
        """
        # Importing mpv at the top causes a segfault when creating an MpvPlayer
        # from Ene, so it's here now
        import mpv
        self.player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
        self.eof = Event()
        self.closed = False
        self.setup_listeners()

    def play(self, episode: Episode):
        """
        Plays the media file given by path

        Args:
            episode: The location of the media file to play
        """
        self.player.play(str(episode.path))

    def stop(self):
        self.player.terminate()

    def setup_listeners(self):
        """
        Attaches listeners for when the MPV instance gets terminated or reaches the end
        """

        @self.player.event_callback('shutdown')
        def on_shutdown(event):  # pylint: disable=unused-argument,unused-variable
            self.stop()
            self.closed = True

        @self.player.event_callback('end_file')
        def on_file_end(event):  # pylint: disable=unused-argument,unused-variable
            self.eof.set()

    def wait_for_playback_end(self):
        """
        Waits until the media stream reaches end of file
        """
        self.eof.wait()

    def needs_destruction(self):
        return self.closed


class GenericPlayer(AbstractPlayer):
    """
    For unsupported players, we can attempt to launch them with a subprocess
    and accept that we can't control them
    """

    def __init__(self, path):
        self.player_path = path
        self.player = None

    def play(self, episode):
        """
        Plays the media file given by path

        Args:
            episode: The location of the media file to play
        """
        if self.player is None:
            self.player = subprocess.Popen([self.player_path, episode.path])

    def stop(self):
        if self.player is not None:
            self.player.terminate()

    def wait_for_playback_end(self):
        if self.player is not None:
            self.player.wait()

    def needs_destruction(self):
        return True


def get_player(config):
    """
    Gets the appropriate player for the user based off the config option

    Args:
        config:
            The configuration to pull options from

    Returns:
        A player class based off AbstractPlayer
    """
    option = config.get('Player')
    if option == 'vlc':
        if config.get('VLC HTTP Interface'):
            return HttpVlcPlayer('127.0.0.1:8080')
        return VlcPlayer()
    elif option == 'mpv':
        return MpvPlayer()
    else:
        return GenericPlayer(config.get('Player Path'))
