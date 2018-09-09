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

from datetime import date
from time import time
from typing import Dict, Optional, Union

import attr

from util import method_dispatch
from .enums import MediaListStatus


@attr.s(auto_attribs=True, slots=True)
class FuzzyDate:
    """
    Date object that allows for incomplete date values (fuzzy).

    Args:
        year: Numeric Year (2017)
        month: Numeric Month (3)
        day: Numeric Day (24)
    """
    year: int = None
    month: int = None
    day: int = None

    def __iter__(self):
        yield self.year
        yield self.month
        yield self.day

    def as_date(self) -> Optional[date]:
        """
        Convert this fuzzy date to a python date.

        Returns:
            The fuzzy date as a date
        """
        try:
            res = date(year=self.year, month=self.month, day=self.day)
        except (ValueError, TypeError):
            return None
        return res

    @classmethod
    def from_date(cls, date_: date) -> 'FuzzyDate':
        """

        Args:
            date_:

        Returns:

        """
        return cls(date_.year, date_.month, date_.day)

    @classmethod
    def from_dict(cls, dict_: dict) -> 'FuzzyDate':
        return cls(
            dict_.get('year'),
            dict_.get('month'),
            dict_.get('day')
        )


@attr.s(auto_attribs=True, slots=True)
class MediaList:
    """
    List entry of anime or manga.

    Args:
        id: The id of the list entry
        media_id: The id of the media
        status: The watching/reading status
        score: The score of the entry
        progress: The amount of episodes/chapters consumed by the user
        repeat: The amount of times the user has rewatched/read the media
        private: If the entry should only be visible to authenticated user
        notes: Text notes
        custom_lists: Map of booleans for which custom lists the entry are in
        started_at: When the entry was started by the user
        completed_at: When the entry was completed by the user
    """
    id: int
    media_id: int
    _status: Optional[Union[str, MediaListStatus]] = None
    score: Optional[float] = None
    progress: Optional[int] = None
    repeat: Optional[int] = None
    private: Optional[bool] = None
    notes: Optional[str] = None
    custom_lists: Optional[Dict[str, bool]] = None
    _started_at: Optional[Union[dict, FuzzyDate, date]] = None
    _completed_at: Optional[Union[dict, FuzzyDate, date]] = None

    @property
    def status(self) -> Optional[MediaListStatus]:
        if not self._status:
            return None
        if isinstance(self._status, str):
            self._status = MediaListStatus[self._status]
        return self._status

    @status.setter
    def status(self, value):
        if value is None or isinstance(value, (str, MediaListStatus)):
            self._status = value
        else:
            raise TypeError("status must be None, a str, or a MediaListStatus.")

    @method_dispatch
    def _get_date(self, value, name):
        return value

    @_get_date.register
    def _(self, value: Dict, name):
        val = FuzzyDate.from_dict(value)
        setattr(self, name, val)
        return val

    @_get_date.register
    def _(self, value: date, name):
        val = FuzzyDate.from_date(value)
        setattr(self, name, val)
        return val

    def _set_date(self, value, name):
        if value is None or isinstance(value, (FuzzyDate, date, Dict)):
            setattr(self, name, value)
        else:
            raise TypeError(f"{name} must be None, a dict, a FuzzyDate, or a date.")

    @property
    def started_at(self) -> Optional[FuzzyDate]:
        return self._get_date(self._started_at, '_started_at')

    @started_at.setter
    def started_at(self, value):
        self._set_date(value, '_started_at')

    @property
    def completed_at(self) -> Optional[FuzzyDate]:
        return self._get_date(self._completed_at, '_completed_at')

    @completed_at.setter
    def completed_at(self, value):
        self._set_date(value, '_completed_at')

    def update(self, api) -> Optional[dict]:
        """
        Update the media list entry.

        Args:
            api: The API object

        Returns:
            Updated media list entry values
        """
        return api.update_media_list_entry(
            media_id=self.media_id,
            status=self.status,
            score=self.score,
            progress=self.progress,
            repeat=self.repeat,
            private=self.private,
            notes=self.notes,
            custom_lists=self.custom_lists,
            started_at=self.started_at,
            completed_at=self.completed_at
        )


@attr.s(slots=True, auto_attribs=True)
class AiringEpisode:
    id: int
    airing_at: int
    episode: int
    media_id: int

    @property
    def time_until_airing(self) -> int:
        return int(self.airing_at - time())


@attr.s(slots=True, auto_attribs=True)
class Studio:
    id: int
    name: str
