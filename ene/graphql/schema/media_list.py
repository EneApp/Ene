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

from collections import UserDict
from datetime import date
from typing import Dict

import attr
from option import NONE, Option, Some, maybe

from graphql.schema.enums import MediaListStatus


@attr.s(slots=True, frozen=True)
class MediaList(UserDict):

    @property
    def id(self) -> int:
        return self['id']

    @property
    def media_id(self) -> int:
        return self['mediaId']

    @property
    def status(self) -> Option[MediaListStatus]:
        status = self.get('status')
        if not status:
            return NONE
        return Some(MediaListStatus[status])

    @property
    def score(self) -> Option[float]:
        return maybe(self.get('score'))

    @property
    def progress(self) -> Option[int]:
        return maybe(self.get('progress'))

    @property
    def repeat(self) -> Option[int]:
        return maybe(self.get('repeat'))

    @property
    def private(self) -> Option[int]:
        return maybe(self.get('private'))

    @property
    def notes(self) -> Option[str]:
        return maybe(self.get('notes'))

    @property
    def custom_lists(self) -> Option[Dict[str, bool]]:
        return maybe(self.get('customLists'))

    @property
    def started_at(self) -> Option[date]:
        return maybe(self.get('startedAt')).map(lambda date_dict: date(**date_dict))

    @property
    def completed_at(self) -> Option[date]:
        return maybe(self.get('completedAt')).map(lambda date_dict: date(**date_dict))
