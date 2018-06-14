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
import mpv
from time import sleep


class VlcPlayer:
    def __init__(self):
        self.process = subprocess.Popen(['vlc', '-I', 'rc'], stdin=subprocess.PIPE)

    def write_cmd(self, cmd):
        # TODO: Find a better way to prevent this from possibly deadlocking or find a way to use Popen.Communicate()
        sleep(1)
        self.process.stdin.write(cmd + b'\n')
        self.process.stdin.flush()

    def add(self, path):
        self.write_cmd(b'add ' + path)

    def get_title(self):
        self.write_cmd(b'get_title')

    def stop(self):
        self.write_cmd(b'stop')


class MpvPlayer:
    def __init__(self):
        """
        Sets up a new MPV instance with the default keybindings
        """
        self.player = mpv.MPV(input_default_bindings=True, input_vo_keyboard=True)
        self.setup_listeners()

    def play(self, path):
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
            # TODO: When this event is raised is when we should update anilist
            self.stop()
            print('End of file reached.')

    def wait_for_pause(self):
        """
        Waits until the media stream is paused
        """
        self.player.wait_for_property('pause', lambda x: x is True)

