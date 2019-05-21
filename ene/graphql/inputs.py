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

from collections import UserDict
from datetime import date
from typing import Dict

import attr

from graphql.schema.enums import MediaListStatus


@attr.s(slots=True, init=False)
class UpdateMediaListEntryInput(UserDict):
    def __init__(self, media_id: int):
        super().__init__()
        self['mediaId'] = media_id

    def status(self, status: MediaListStatus) -> UpdateMediaListEntryInput:
        self['status'] = status.name
        return self

    def score(self, score: float) -> UpdateMediaListEntryInput:
        self['score'] = score
        return self

    def progress(self, progress: int) -> UpdateMediaListEntryInput:
        self['progress'] = progress
        return self

    def custom_lists(self, custom_lists: Dict[str, bool]) -> UpdateMediaListEntryInput:
        self['customLists'] = custom_lists
        return self

    def private(self, private: bool) -> UpdateMediaListEntryInput:
        self['private'] = private
        return self

    def notes(self, notes: str) -> UpdateMediaListEntryInput:
        self['notes'] = notes
        return self

    def started_at(self, started_at: date) -> UpdateMediaListEntryInput:
        self['startedAt'] = {
            'year': started_at.year,
            'month': started_at.month,
            'day': started_at.day
        }
        return self

    def completed_at(self, completed_at: date) -> UpdateMediaListEntryInput:
        self['completedAt'] = {
            'year': completed_at.year,
            'month': completed_at.month,
            'day': completed_at.day
        }
        return self

    def repeat(self, repeat: int) -> UpdateMediaListEntryInput:
        self['repeat'] = repeat
        return self
