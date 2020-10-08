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

from sys import argv

new_file = []
comment = []
start = False
trip = '"""'

with open(argv[1]) as f:
    for line in f:
        line = line.strip('\n')
        strip = line.strip()
        leading_space = ' ' * (len(line) - len(line.lstrip(' ')))

        if strip.startswith(trip) and strip.endswith(trip) and strip != trip:
            new_file.append('{}# {}'.format(leading_space, strip.replace(trip, '')))
        elif line.strip().endswith(trip) and start:
            new_file.append('\n'.join(comment))
            start = False
            del comment[:]
        elif line.strip().startswith(trip):
            start = True
        elif start:
            comment.append(f'{leading_space}# {strip}')
        else:
            new_file.append(line)
print('\n'.join(new_file))
