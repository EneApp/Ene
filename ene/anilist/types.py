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

from abc import ABCMeta, abstractmethod
from datetime import date
from functools import lru_cache
from time import time
from typing import Optional

from dataclasses import dataclass

from ene.anilist.api import API
from ene.anilist.enums import MediaType, MediaFormat, MediaStatus
from ene.util import cache


class Resource(metaclass=ABCMeta):

    def __init__(self, api, data=None):
        self.api = api
        self._cache = data or {}
        self._timeout = {}
        now = time()
        for key in self._cache:
            self._timeout[key] = now

    @property
    @abstractmethod
    def _key(self):
        raise NotImplementedError()

    @abstractmethod
    def _build_query(self, format):
        raise NotImplementedError()

    def _request(self, format, variables=None):
        query = self._build_query(format)
        res = self.api.query(query, variables)
        return res['data'][self.__class__.__name__]

    def _request_scalar(self, name):
        return self._request(' ' * 16 + name).get(name)

    def _request_enum(self, cls, name):
        res = self._request(' ' * 16 + name).get(name)
        if res:
            return getattr(cls, res)

    def __hash__(self):
        return hash(self._key)

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self._key == other._key
        return NotImplemented


@dataclass(unsafe_hash=True, order=True)
class MediaTitle:
    romaji: str
    english: str
    native: str
    userPreferred: str
    __slots__ = ('romaji', 'english', 'native', 'userPreferred')


class Media(Resource):
    def __init__(self, id_: int, type_: MediaType, api: API, data=None):
        self.id = id_
        self.type = type_
        super().__init__(api, data)

    @property
    @cache
    def idMal(self) -> Optional[int]:
        """The mal id of the media"""
        return self._request_scalar('idMal')

    @property
    @cache
    def title(self) -> Optional[MediaTitle]:
        """The official titles of the media in various languages"""
        res = self._request("""\
                title {
                    romaji
                    english
                    native
                    userPreferred
                }""").get('title')
        if res:
            return MediaTitle(**res)

    @property
    @cache
    def format(self) -> Optional[MediaFormat]:
        """The format the media was released in"""
        return self._request_enum(MediaFormat, 'format')

    @property
    @cache
    def status(self) -> Optional[MediaStatus]:
        """The current releasing status of the media"""
        return self._request_enum(MediaStatus, 'status')

    @cache
    def description(self, asHtml: bool = False) -> Optional[str]:
        """
        Short description of the media's story and characters
        Args:
            asHtml:
                Return the string in pre-parsed html instead of markdown
        """
        name = 'description'
        return self._request(f'{" " * 16}{name}(asHtml: {str(asHtml).lower()})').get(name)

    @property
    @cache
    def startDate(self) -> Optional[date]:
        """The first official release date of the media"""
        res = self._request("""\
                startDate {
                    year
                    month
                    day
                }""").get('startDate')
        if res:
            return date(**res)

    @property
    @cache
    def endDate(self) -> Optional[date]:
        """The last official release date of the media"""
        res = self._request("""\
                endDate {
                    year
                    month
                    day
                }""").get('endDate')
        if res:
            return date(**res)

    @property
    def _key(self):
        return (self.id, self.type)

    @lru_cache(None)
    def _build_query(self, format):
        return """\
        query {
            Media (id: %d, type: %s) {
%s
            }
        }""" % (self.id, self.type.name, format)


if __name__ == '__main__':
    m = Media(15125, MediaType.ANIME, API())
