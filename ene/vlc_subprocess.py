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


class VlcPlayer:
    def __init__(self):
        self.process = subprocess.Popen(['vlc', '-I', 'rc'], stdin=subprocess.PIPE)

    def write_cmd(self, cmd):
        # TODO: Prevent this from possibly deadlocking or find a way to use Popen.Communicate()
        self.process.stdin.write(cmd + b'\n')
        self.process.stdin.flush()

    def add(self, path):
        self.write_cmd(b'add ' + path)

    def get_title(self):
        self.write_cmd(b'get_title')

    def stop(self):
        self.write_cmd(b'stop')
