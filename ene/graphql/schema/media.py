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
from typing import List

import attr
from option import NONE, Option, Some, maybe

from graphql.schema.airing_episode import AiringEpisode
from graphql.schema.enums import MediaFormat, MediaSeason, MediaStatus, MediaType
from graphql.schema.media_list import MediaList
from graphql.schema.studio import Studio


@attr.s(repr=False, slots=True, init=False)
class Media(UserDict):
    def __init__(self, data):
        super().__init__(data)

    @property
    def id(self) -> int:
        return self.data['id']

    @property
    def title(self) -> Option[str]:
        return maybe(self.data['title']).get('userPreferred')

    @property
    def type(self) -> Option[MediaType]:
        return maybe(MediaType.get(self.data['type']))

    @property
    def format(self) -> Option[MediaFormat]:
        return maybe(MediaFormat.get(self.data['format']))

    @property
    def status(self) -> Option[MediaStatus]:
        return maybe(MediaStatus.get(self.data['status']))

    @property
    def description(self) -> Option[str]:
        return maybe(self.data['description'])

    @property
    def start_date(self) -> Option[date]:
        return maybe(self.data['startDate']).map(lambda start_date: date(**start_date))

    @property
    def end_date(self) -> Option[date]:
        return maybe(self.data['endDate']).map(lambda end_date: date(**end_date))

    @property
    def season(self) -> Option[MediaSeason]:
        return maybe(MediaSeason.get(self.data['season']))

    @property
    def cover_image(self) -> Option[str]:
        return maybe(self.data['coverImage']).get('large')

    @property
    def banner_image(self) -> Option[str]:
        return maybe(self.data['bannerImage'])

    @property
    def genres(self) -> List[str]:
        return self.data['genres'] or []

    @property
    def is_adult(self) -> bool:
        return self.data['isAdult'] or False

    @property
    def average_score(self) -> Option[int]:
        return maybe(self.data['averageScore'])

    @property
    def popularity(self) -> Option[int]:
        return maybe(self.data['popularity'])

    @property
    def media_list_entry(self) -> Option[MediaList]:
        media_list_entry = self.data['mediaListEntry']
        return Some(MediaList(media_list_entry)) if media_list_entry else NONE

    @property
    def next_airing_episode(self) -> Option[AiringEpisode]:
        if self.type.unwrap_or(None) != MediaType.ANIME:
            raise NotImplementedError('Only available for anime.')

        airing_episode = self.data['nextAiringEpisode']
        return Some(AiringEpisode(
            id=airing_episode['id'],
            airing_at=airing_episode['airingAt'],
            episode=airing_episode['episode'],
            media_id=self.id
        )) if airing_episode else NONE

    @property
    def studio(self) -> Option[Studio]:
        studios = maybe(self.data['studios']).get('edges').unwrap_or([])
        for studio in studios:
            if studio['isMain']:
                node = studio['node']
                return Some(Studio(id=node['id'], name=node['name']))
        return NONE

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id}, data={self.data!r})'
