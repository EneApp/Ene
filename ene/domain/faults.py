#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2019 Peijun Ma, Justin Sedge
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

from __future__ import annotations

from typing import List

import attr


@attr.s(frozen=True, slots=True, auto_attribs=True)
class Fault:
    code: str
    description: str

    def to_faults(self) -> Faults:
        return Faults([self])


@attr.s(frozen=True, slots=True, auto_attribs=True, init=False)
class HTTPFault(Fault):
    code: str
    description: str

    def __init__(self, code: int, description: str) -> None:
        super().__init__(f'HTTP_FAULT Code: {code}', description)


@attr.s(frozen=True, slots=True, auto_attribs=True)
class Faults:
    faults: List[Fault] = []

    def add_fault(self, fault: Fault) -> Faults:
        self.faults.append(fault)
        return self

    def add_from_str(self, code: str, description: str) -> Faults:
        self.faults.append(Fault(code, description))
        return self
