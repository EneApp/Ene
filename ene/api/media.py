#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018 Peijun Ma, Justin Sedge
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your Option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path
from typing import List, Union

import attr
from option import NONE, Option, maybe, some

from ene.util import get_resource
from .enums import MediaFormat, MediaSeason, MediaStatus, MediaType
from .types_ import AiringEpisode, FuzzyDate, MediaList, Studio


@attr.s(repr=False, slots=True, auto_attribs=True)
class Media:
    data: dict
    cache_home: Union[str, Path]

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
    def start_date(self) -> Option[FuzzyDate]:
        return maybe(self.data['startDate']).map(FuzzyDate.from_dict)

    @property
    def end_date(self) -> Option[FuzzyDate]:
        return maybe(self.data['endDate']).map(FuzzyDate.from_dict)

    @property
    def season(self) -> Option[MediaSeason]:
        return maybe(MediaSeason.get(self.data['season']))

    @property
    def cover_image(self) -> Option[Path]:
        return maybe(self.data['coverImage']).get('large').map(self._get_resource)

    @property
    def banner_image(self) -> Option[Path]:
        return maybe(self.data['bannerImage']).map(self._get_resource)

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
        return some(MediaList(
            id=media_list_entry['id'],
            media_id=self.id,
            status=media_list_entry.get('status'),
            score=media_list_entry.get('score'),
            progress=media_list_entry.get('progress'),
            repeat=media_list_entry.get('repeat'),
            private=media_list_entry.get('private'),
            notes=media_list_entry.get('notes'),
            custom_lists=media_list_entry.get('customLists'),
            started_at=media_list_entry.get('startedAt'),
            completed_at=media_list_entry.get('completedAt')
        )) if media_list_entry else NONE

    @property
    def next_airing_episode(self) -> Option[AiringEpisode]:
        if self.type != MediaType.ANIME:
            raise NotImplementedError('Only available for anime.')
        airing_episode = self.data['nextAiringEpisode']
        return some(AiringEpisode(
            id=airing_episode['id'],
            airing_at=airing_episode['airingAt'],
            episode=airing_episode['episode'],
            media_id=self.id
        )) if airing_episode else NONE

    @property
    def studio(self) -> Option[Studio]:
        studios = maybe(self.data['studios']).get('nodes').unwrap_or(None)
        if studios:
            node = studios[0]
            return some(Studio(id=node['id'], name=node['name']))
        return NONE

    def _get_resource(self, url) -> Path:
        return get_resource(url, self.cache_home)

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id}, data={self.data!r})'
