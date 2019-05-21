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
from typing import List

import attr

from graphql.schema.enums import MediaFormat, MediaSeason, MediaSort, MediaStatus


@attr.s(slots=True, init=False)
class ListAnimeFilter(UserDict):
    def __init__(self):
        super().__init__()

    def adult(self, is_adult: bool) -> ListAnimeFilter:
        self['isAdult'] = is_adult
        return self

    def search(self, search: str) -> ListAnimeFilter:
        self['search'] = search
        return self

    def format(self, format: MediaFormat) -> ListAnimeFilter:
        self['format'] = format.name
        return self

    def status(self, status: MediaStatus) -> ListAnimeFilter:
        self['status'] = status.name
        return self

    def season(self, season: MediaSeason) -> ListAnimeFilter:
        self['season'] = season.name
        return self

    def on_list(self, on_list: bool) -> ListAnimeFilter:
        self['onList'] = on_list
        return self

    def licensed_by(self, licensed_by: List[str]) -> ListAnimeFilter:
        self['licensedBy'] = licensed_by
        return self

    def included_genres(self, included_genres: List[str]) -> ListAnimeFilter:
        self['includedGenres'] = included_genres
        return self

    def excluded_genres(self, excluded_genres: List[str]) -> ListAnimeFilter:
        self['excludedGenres'] = excluded_genres
        return self

    def included_tags(self, included_tags: List[str]) -> ListAnimeFilter:
        self['includedTags'] = included_tags
        return self

    def excluded_tags(self, excluded_tags: List[str]) -> ListAnimeFilter:
        self['excludedTags'] = excluded_tags
        return self

    def sort(self, sort: List[MediaSort]) -> ListAnimeFilter:
        self['sort'] = [s.name for s in sort]
        return self

    def year(self, year: int):
        self['year'] = f'{year}%'
        return self

    def year_range(self, from_year: int, to_year: int) -> ListAnimeFilter:
        if from_year == to_year:
            return self.year(from_year)
        self['yearGreater'] = from_year * 10000
        self['yearLesser'] = to_year * 10000
        return self
