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

from abc import abstractmethod, ABC
from datetime import date
from time import time
from typing import Optional, Hashable, Type, List, Iterable, Union

from ene.anilist.api import API
from ene.anilist.enums import MediaType, MediaFormat, MediaStatus
from ene.util import cache, strip_html

Field = Union[str, dict]
Fields = List[Field]
Opt = Optional


class Resource(ABC):
    """
    Base class for all requestable types from the anilist API
    """
    __slots__ = ('api', '_cache', '_timeout', '_base_query')

    def __init__(self, api: API, base_query: str, data: Opt[dict] = None):
        self.api = api
        self._base_query = base_query
        self._cache = data or {}
        self._timeout = {}
        now = time()
        for key in self._cache:
            self._timeout[key] = now

    def _format_fields(self, fields: Fields, padding: int = 8) -> Iterable[str]:
        """
        Convert request fields into GraphQL format
        Args:
            fields:
                List of fields,
                can be a str for simple field or dict for more complex fields
            padding: Left padding of the output string
        Yields:
            Lines of text for the resulting string
        """
        spaces = padding * ' '
        for field in fields:
            if isinstance(field, str):
                yield f'{spaces}{field}'
                continue
            args = field.get('args', '')
            base = f'{spaces}{field["name"]}'
            subfields = field.get('subfields')
            if args:
                base = f'{base} ({args})'
            if subfields:
                yield base + ' {'
                yield from self._format_fields(subfields, padding + 4)
                yield spaces + '}'
            else:
                yield base

    def _build_query(self, fields: Fields, params: Opt[dict] = None) -> str:
        """
        Build request query
        Args:
            params: Parameters used in the request in {name: type} format
        Returns:
            The request query
        """
        if params:
            params = f'({", ".join(f"${name}: {type_}" for name, type_ in params.items())})'
        else:
            params = ''
        return self._base_query % (params, '\n'.join(self._format_fields(fields)))

    def _request(
            self,
            fields: Fields,
            params: Opt[dict] = None,
            variables: Opt[dict] = None
    ) -> dict:
        """
        Make a request
        Args:
            fields:
                List of fields,
                can be a str for simple field or dict for more complex fields
            params: Parameters used in the request in {name: type} format
            variables: variables for the query
        Returns:
            The response data
        """
        query = self._build_query(fields, params)
        res = self.api.query(query, variables)
        return res.get('data', {}).get(self.__class__.__name__, {})

    def _request_scalar(self, name: str):
        """
        Request a single scalar value
        Args:
            name: Name of the salar
        Returns:
            The value requested
        """
        return self._request([name]).get(name)

    def _request_enum(self, enum_type: Type, name: str):
        """
        Request an enum value
        Args:
            enum_type: The type of the enum
            name: The name of the field
        Returns:
            The enum value requested
        """
        res = self._request_scalar(name)
        if res:
            return getattr(enum_type, res)

    @property
    @abstractmethod
    def _key(self) -> Hashable:
        """The key should uniquely identify the instance of a ``Resource``"""
        raise NotImplementedError()

    def __hash__(self):
        return hash(self._key)

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self._key == other._key
        return NotImplemented


class MediaTitle:
    """The official titles of the media in various languages"""
    __slots__ = ('media', '_cache', '_timeout')

    def __init__(self, media):
        self.media = media
        self._cache = {}
        self._timeout = {}

    @cache
    def _request_title(self, stylised: bool = True) -> dict:
        """
        Request title information
        Args:
            stylised: Wether the title is stylised
        Returns:
            Titles of the media in all languages
        """
        args = 'stylised: $stylised'
        return self.media._request(
            [{'name': 'title', 'subfields':
                [{'name': 'romaji', 'args': args},
                 {'name': 'english', 'args': args},
                 {'name': 'native', 'args': args},
                 'userPreferred']
              }],
            {'stylised': 'Boolean'}, {'stylised': stylised}
        ).get('title', {})

    def romaji(self, stylised: bool = True) -> Opt[str]:
        """
        The romanization of the native language title
        Args:
            stylised: Wether the title is stylised
        """
        return self._request_title(stylised).get('romaji')

    def english(self, stylised: bool = True) -> Opt[str]:
        """
        The official english title
        Args:
            stylised: Wether the title is stylised
        """
        return self._request_title(stylised).get('english')

    def native(self, stylised: bool = True) -> Opt[str]:
        """
        Official title in it's native language
        Args:
            stylised: Wether the title is stylised
        """
        return self._request_title(stylised).get('native')

    @property
    def userPreferred(self) -> Opt[str]:
        """
        The currently authenticated users preferred title language.
        Default romaji for non-authenticated
        """
        return self._request_title().get('userPreferred')


class Media(Resource):
    __slots__ = ('_id', '_type', '_title')

    def __init__(self, id_: int, type_: MediaType, api: API, data=None):
        self._id = id_
        self._type = type_
        self._title = MediaTitle(self)
        base_query = """\
query %s {
    Media (id: $id, type: $type) {
%s
    }
}"""
        super().__init__(api, base_query, data)

    @property
    def id(self) -> int:
        """ The id of the media"""
        return self._id

    @property
    @cache
    def idMal(self) -> Opt[int]:
        """The mal id of the media"""
        return self._request_scalar('idMal')

    @property
    def title(self) -> MediaTitle:
        """The official titles of the media in various languages"""
        return self._title

    @property
    def type(self) -> MediaType:
        """The type of the media; anime or manga"""
        return self._type

    @property
    @cache
    def format(self) -> Opt[MediaFormat]:
        """The format the media was released in"""
        return self._request_enum(MediaFormat, 'format')

    @property
    @cache
    def status(self) -> Opt[MediaStatus]:
        """The current releasing status of the media"""
        return self._request_enum(MediaStatus, 'status')

    @cache
    def description(self, asHtml: bool = False) -> Opt[str]:
        """
        Short description of the media's story and characters
        Args:
            asHtml:
                Return the string in pre-parsed html instead of markdown
        """
        res = self._request(
            [{'name': 'description', 'args': 'asHtml: $asHtml'}],
            {'asHtml': 'Boolean'},
            {'asHtml': asHtml}
        ).get('description')
        if res and asHtml:
            return res
        elif res:
            return strip_html(res)

    @property
    @cache
    def startDate(self) -> Opt[date]:
        """The first official release date of the media"""
        res = self._request(
            [{'name': 'startDate', 'subfields': ['year', 'month', 'day']}]
        ).get('startDate')
        if res:
            return date(**res)

    @property
    @cache
    def endDate(self) -> Opt[date]:
        """The last official release date of the media"""
        res = self._request(
            [{'name': 'endDate', 'subfields': ['year', 'month', 'day']}]
        ).get('endDate')
        if res:
            return date(**res)

    @property
    def _key(self):
        return (self.id, self.type)

    def _request(
            self,
            fields: Fields,
            params: Opt[dict] = None,
            variables: Opt[dict] = None
    ) -> dict:
        params = params or {}
        params['id'] = 'Int'
        params['type'] = 'MediaType'
        variables = variables or {}
        variables['type'] = self.type.name
        variables['id'] = self.id
        return super()._request(fields, params, variables)
