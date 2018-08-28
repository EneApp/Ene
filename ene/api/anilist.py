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

"""This module contains anilist API class."""
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from requests import HTTPError, Session

import ene.api
from ene.constants import CLIENT_ID, GRAPHQL_URL, resources
from ene.errors import APIError
from .auth import OAuth
from .enums import MediaFormat, MediaSeason, MediaSort, MediaStatus


class API:
    """
    Handles requests to the Anilist API
    """

    def __init__(self, data_home: Path):
        self.token = OAuth.get_token(data_home, CLIENT_ID, '127.0.0.1', 50000)
        self.session = Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.queries = {}
        for name in resources.contents(ene.api):
            if name.endswith('.graphql'):
                self.queries[name] = resources.read_text(ene.api, name)

    def query(self, query: str, variables: Optional[dict] = None) -> dict:
        """
        Makes HTTP request to the Anilist API

        Args:
            query: The GraphQL query to POST to the API
            variables: variables for the query, can be None

        Returns:
            The API response

        Raises:
            APIHTTPError if request failed
        """
        post_json = {'query': query}
        if variables:
            post_json['variables'] = variables

        res = self.session.post(GRAPHQL_URL, json=post_json)
        try:
            res.raise_for_status()
        except HTTPError as http_ex:
            try:
                json = res.json()
            except Exception as e:  # pylint: disable=W0703
                msg = f'{http_ex}\n{e}'
            else:
                msg_lst = []
                errors = json.get('errors', [])
                if errors:
                    for err in errors:
                        msg_lst.append(err.get('message'))
                msg = '\n'.join(m for m in msg_lst if m) or str(http_ex)
            raise APIError(res.status_code, msg)
        else:
            return res.json()

    def query_pages(
            self,
            query: str,
            per_page: int,
            variables: Optional[dict] = None
    ) -> Iterable[dict]:
        """
        Make paged requests to the Anilist API

        Args:
            query: The GraphQL query to POST to the API
            per_page: Number of items per page
            variables: variables for the query, can be None

        Yields:
            Each page of the API response

        Raises:
            APIHTTPError if request failed
        """
        variables = variables.copy() if variables else {}
        variables['page'] = 1
        variables['perPage'] = per_page

        while True:
            res = self.query(query, variables)
            has_next = res['data']['Page']['pageInfo']['hasNextPage']
            yield res
            if not has_next:
                return
            variables['page'] += 1

    def browse_anime(  # pylint: disable=R0914
            self,
            page=1,
            *,
            is_adult: bool = None,
            search: str = None,
            format_: MediaFormat = None,
            status: MediaStatus = None,
            season: MediaSeason = None,
            year_range: Tuple[int, int] = None,
            on_list: bool = None,
            licensed_by: List[str] = None,
            included_genres: List[str] = None,
            excluded_genres: List[str] = None,
            included_tags: List[str] = None,
            excluded_tags: List[str] = None,
            sort: List[MediaSort] = None
    ) -> Iterable[dict]:
        """
        Browse anime by the given filters.

        Args:
            page: which page of the anime to return
            is_adult: Filter by if the media's intended for 18+ adult audiences
            search: Filter by search query
            format_: Filter by the media's format
            status: Filter by the media's current release status
            season: The season the media was initially released in
            year_range: The year range the media is ranked within
            on_list: Filter by the media on the authenticated user's lists
            licensed_by: Filter media by sites with a online streaming license
            included_genres: Filter by the media's genres
            excluded_genres: Filter by the media's genres
            included_tags: Filter by the media's tags
            excluded_tags: Filter by the media's tags
            sort: The order the results will be returned in

        Yields:
            The anime returned
        """
        variables = {k: v for k, v in {
            'page': page,
            'isAdult': is_adult,
            'search': search,
            'format': format_,
            'status': status,
            'season': season,
            'onList': on_list,
            'licensedBy': licensed_by,
            'includedGenres': included_genres,
            'excludedGenres': excluded_genres,
            'includedTags': included_tags,
            'excludedTags': excluded_tags,
        }.items() if v is not None}
        if sort:
            variables['sort'] = [s.name for s in sort]
        if year_range:
            start, fin = year_range
            if start == fin:
                variables['year'] = f'{start}%'
            else:
                variables['yearLesser'] = start * 10000
                variables['yearGreater'] = fin * 10000
        yield from self.query(self.queries['browse.graphql'], variables)['data']['Page']['media']

    @lru_cache(maxsize=None)
    def get_genres(self) -> List[str]:
        """
        Get all genres

        Returns:
            List of genres
        """
        query = '{GenreCollection}'
        res = self.query(query)
        return res['data']['GenreCollection']

    @lru_cache(maxsize=None)
    def get_tags(self) -> List[dict]:
        """
        Get all tags

        Returns:
            List of tags
        """
        query = """\
{
    MediaTagCollection {
        id
        name
        category
        isAdult
        isGeneralSpoiler
        isMediaSpoiler
    }
}"""
        res = self.query(query)
        return res['data']['MediaTagCollection']
