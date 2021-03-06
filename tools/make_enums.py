#!/usr/bin/env python3
#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2020 Peijun Ma, Justin Sedge
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

"""Generate python enums from graphqls enums"""

import re
import sys

copyright = '''\
#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2020 Peijun Ma, Justin Sedge
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

# pylint: skip-file
"""This file is generated by a tool, see tools/make_enums.py"""

from enum import Enum, auto


class GettableEnum(Enum):
    @classmethod
    def get(cls, key, default=None):
        try:
            res = cls[key]
        except KeyError:
            res = default
        return res
'''

if __name__ == '__main__':
    usage = f"Usage: {__file__} FILE"

    if len(sys.argv) != 2:
        print(usage)
        sys.exit(1)

    file = sys.argv[1]
    start = False

    current_name = None
    current_items = []
    print(copyright)
    with open(file) as f:
        for line in f:
            name = re.match(r'enum (\w+) {', line)
            if name:
                start = True
                current_name = name.groups()[0]
            elif start and line.strip() == '}':
                print(f'class {current_name}(GettableEnum):')
                for item in current_items:
                    print(f'    {item} = auto()')
                print('\n')
                start = False
                current_items.clear()
            elif start:
                strip = line.strip()
                if not strip or strip.startswith('#'):
                    continue
                item = re.match(r'(\w+)\s*#*.*', strip)
                current_items.append(item.groups()[0])
