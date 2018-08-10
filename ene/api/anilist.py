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
from typing import Iterable, List, Optional

from requests import HTTPError, post

import ene.api
from ene.constants import CLIENT_ID, GRAPHQL_URL, resources
from ene.errors import APIError
from .auth import OAuth
from .enums import MediaSeason, MediaSort


# TODO: add caching
# TODO: add threading
class API:
    """
    Handles requests to the Anilist API
    """

    def __init__(self):
        self.token = OAuth.get_token(CLIENT_ID, '127.0.0.1', 50000)
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
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

        res = post(GRAPHQL_URL, json=post_json, headers=self.headers)
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

    def get_season_anime(
            self,
            season: MediaSeason,
            year: int,
            per_page: int = 20,
            sort: Optional[List[MediaSort]] = None
    ) -> Iterable[dict]:
        """
        Query all anime of a given season

        Args:
            season: The season
            year: The year for the season
            per_page: How many anime per page of the response
            sort: List of keys to sort by, defaults to popularity decending. See
                https://anilist.github.io/ApiV2-GraphQL-Docs/mediasort.doc.html

        Yields:
            All anime in that season

        Raises:
            APIHTTPError if request failed
        """
        sort = sort or [MediaSort.POPULARITY_DESC.name]
        variables = {
            'season': season.name,
            'seasonYear': year,
            'sort': [s.name for s in sort]
        }
        for page in self.query_pages(self.queries['season.graphql'], per_page, variables):
            for anime in page['data']['Page']['media']:
                yield anime

    def get_genres(self) -> List[str]:
        """
        Get all genres
        Returns:
            List of genres
        """
        query = '{GenreCollection}'
        res = self.query(query)
        return res['data']['GenreCollection']

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
