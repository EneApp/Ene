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

import subprocess
from abc import ABC, abstractmethod
from shutil import which
from threading import Event
from time import sleep

import mpv
import vlc

from ene.constants import IS_MAC, IS_WIN


class AbstractPlayer(ABC):
    @abstractmethod
    def play(self, path):
        """
        Plays the media file given by path
        :param path: The location of the media file to play
        """
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()

    @abstractmethod
    def wait_for_playback_end(self):
        raise NotImplementedError()


class VlcPlayer(AbstractPlayer):
    """
    An implementation of the VLC player using the python-vlc library
    """

    def __init__(self):
        self.instance = vlc.Instance('--extraintf=hotkeys')
        self.player = self.instance.media_player_new()
        self.player.video_set_key_input(True)
        self.player.video_set_mouse_input(True)

    def play(self, path):
        media = self.instance.media_new(path)
        self.player.set_media(media)
        self.player.play()

    def stop(self):
        self.player.stop()

    def wait_for_playback_end(self):
        sleep(30)


class RcVlcPlayer(AbstractPlayer):
    """
    An implementation of the VLC player using the rc interface and passing commands to stdin
    """

    def __init__(self, binary=None):
        if not binary and IS_WIN:
            binary = which('vlc.exe')
        elif not binary:
            binary = which('vlc')

        args = [binary, '-I', 'rc']
        if IS_MAC:
            # mac is special
            args.append('--extraintf=macosx')
        else:
            args.append('--extraintf=qt')
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, universal_newlines=True)

    def write_cmd(self, cmd):
        """
        Prepares and writes a command to the vlc rc interface on STDIN
        :param cmd:
        :return:
        """
        # TODO: Find a better way to prevent this from possibly deadlocking or find a way to use Popen.Communicate() # noqa: E501
        sleep(1)
        self.process.stdin.write(cmd + '\n')
        self.process.stdin.flush()

    def play(self, path):
        """
        Plays the media file given by path
        :param path: The location of the media file to play
        """
        self.write_cmd('add ' + path)

    def get_title(self):
        self.write_cmd('get_title')

    def stop(self):
        self.write_cmd('stop')

    def wait_for_playback_end(self):
        sleep(10)


class MpvPlayer(AbstractPlayer):
    """
    An implementation of the MPV player using the python-mpv library
    """

    def __init__(self):
        """
        Sets up a new MPV instance with the default keybindings
        """
        self.player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
        self.eof = Event()
        self.setup_listeners()

    def play(self, path):
        """
        Plays the media file given by path
        :param path: The location of the media file to play
        """
        self.player.play(path)

    def stop(self):
        self.player.terminate()

    def setup_listeners(self):
        """
        Attaches listeners for when the MPV instance gets terminated or reaches the end
        """

        @self.player.event_callback('shutdown')
        def on_shutdown(event):
            self.stop()

        @self.player.event_callback('end_file')
        def on_file_end(event):
            self.eof.set()

    def wait_for_playback_end(self):
        """
        Waits until the media stream reaches end of file
        """
        self.eof.wait()


class GenericPlayer(AbstractPlayer):
    """
    For unsupported players, we can attempt to launch them with a subprocess
    and accept that we can't control them
    """

    def __init__(self, path):
        self.player_path = path
        self.player = None

    def play(self, path):
        """
        Plays the media file given by path
        :param path: The location of the media file to play
        """
        if self.player is None:
            self.player = subprocess.Popen([self.player_path, path])

    def stop(self):
        if self.player is not None:
            self.player.terminate()

    def wait_for_playback_end(self):
        if self.player is not None:
            self.player.wait()
