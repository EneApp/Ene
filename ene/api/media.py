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
from typing import List, Union

import attr
from result import Ok

from constants import ERR_NONE
from ene.util import Maybe, get_resource, maybe
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
    def title(self) -> Maybe[str]:
        return maybe((self.data['title'] or {}).get('userPreferred'))

    @property
    def type(self) -> Maybe[MediaType]:
        return maybe(MediaType.get(self.data['type']))

    @property
    def format(self) -> Maybe[MediaFormat]:
        return maybe(MediaFormat.get(self.data['format']))

    @property
    def status(self) -> Maybe[MediaStatus]:
        return maybe(MediaStatus.get(self.data['status']))

    @property
    def description(self) -> Maybe[str]:
        return maybe(self.data['description'])

    @property
    def start_date(self) -> Maybe[FuzzyDate]:
        start_date = self.data['startDate']
        return Ok(FuzzyDate.from_dict(start_date)) if start_date else ERR_NONE

    @property
    def end_date(self) -> Maybe[FuzzyDate]:
        end_date = self.data['endDate']
        return Ok(FuzzyDate.from_dict(end_date)) if end_date else ERR_NONE

    @property
    def season(self) -> Maybe[MediaSeason]:
        return maybe(MediaSeason.get(self.data['season']))

    @property
    def cover_image(self) -> Maybe[Path]:
        url = (self.data['coverImage'] or {}).get('large')
        return Ok(get_resource(url, self.cache_home)) if url else ERR_NONE

    @property
    def banner_image(self) -> Maybe[Path]:
        url = self.data['bannerImage']
        return Ok(get_resource(url, self.cache_home)) if url else ERR_NONE

    @property
    def genres(self) -> List[str]:
        return self.data['genres'] or []

    @property
    def is_adult(self) -> bool:
        return self.data['isAdult'] or False

    @property
    def average_score(self) -> Maybe[int]:
        return maybe(self.data['averageScore'])

    @property
    def popularity(self) -> Maybe[int]:
        return maybe(self.data['popularity'])

    @property
    def media_list_entry(self) -> Maybe[MediaList]:
        media_list_entry = self.data['mediaListEntry']
        return Ok(MediaList(
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
        )) if media_list_entry else ERR_NONE

    @property
    def next_airing_episode(self) -> Maybe[AiringEpisode]:
        if self.type != MediaType.ANIME:
            raise NotImplementedError('Only available for anime.')
        airing_episode = self.data['nextAiringEpisode']
        return Ok(AiringEpisode(
            id=airing_episode['id'],
            airing_at=airing_episode['airingAt'],
            episode=airing_episode['episode'],
            media_id=self.id
        )) if airing_episode else ERR_NONE

    @property
    def studio(self) -> Maybe[Studio]:
        studios = (self.data['studios'] or {}).get('nodes', [])
        if studios:
            node = studios[0]
            return Ok(Studio(id=node['id'], name=node['name']))
        return ERR_NONE

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id}, data={self.data!r})'
