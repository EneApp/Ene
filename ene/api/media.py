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

from pathlib import Path
from typing import List, Optional, Union

import attr

from ene.util import get_resource
from .enums import MediaFormat, MediaSeason, MediaStatus, MediaType
from .types import FuzzyDate


@attr.s
class Media:
    values: dict
    cache_home: Union[str, Path]

    @property
    def id(self) -> int:
        return self.values['id']

    @property
    def title(self) -> str:
        return self.values['title']['userPreferred']

    @property
    def cover_image(self) -> Optional[Path]:
        img = self.values['coverImage']
        if img:
            url = img.get('large')
            if url:
                return get_resource(url, self.cache_home)

    @property
    def banner_image(self) -> Optional[Path]:
        url = self.values['bannerImage']
        if url:
            return get_resource(url, self.cache_home)

    @property
    def start_date(self) -> Optional[FuzzyDate]:
        start_date = self.values['startDate']
        if start_date:
            return FuzzyDate(
                start_date['year'],
                start_date['month'],
                start_date['day']
            )

    @property
    def end_date(self) -> Optional[FuzzyDate]:
        end_date = self.values['endDate']
        if end_date:
            return FuzzyDate(
                end_date['year'],
                end_date['month'],
                end_date['day']
            )

    @property
    def season(self) -> Optional[MediaSeason]:
        season = self.values['season']
        if season:
            return MediaSeason[season]

    @property
    def description(self) -> Optional[str]:
        return self.values['description']

    @property
    def type(self) -> MediaType:
        return MediaType[self.values['type']]

    @property
    def format(self) -> MediaFormat:
        return MediaFormat[self.values['format']]

    @property
    def status(self) -> MediaStatus:
        return MediaStatus[self.values['status']]

    @property
    def genres(self) -> List[str]:
        return self.values['genres'] or []

    @property
    def is_adult(self) -> bool:
        return self.values['isAdult']

    @property
    def average_score(self) -> Optional[int]:
        return self.values['averageScore']

    @property
    def popularity(self) -> int:
        return self.values['popularity']

    @property
    def media(self) -> Optional:
        return
