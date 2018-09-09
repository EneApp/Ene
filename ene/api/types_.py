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

from typing import Dict, Optional

import attr

from .enums import MediaListStatus


@attr.s(auto_attribs=True)
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


@attr.s(auto_attribs=True)
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
    status: Optional[MediaListStatus] = None
    score: Optional[float] = None
    progress: Optional[int] = None
    repeat: Optional[int] = None
    private: Optional[bool] = None
    notes: Optional[str] = None
    custom_lists: Optional[Dict[str, bool]] = None
    started_at: Optional[FuzzyDate] = None
    completed_at: Optional[FuzzyDate] = None

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
