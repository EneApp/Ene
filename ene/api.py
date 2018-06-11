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
from typing import Iterable, List, Optional

from requests import HTTPError, post

from ene.auth import OAuth
from ene.errors import APIError
from ene.util import load_file

CLIENT_ID = 584
GRAPHQL_URL = 'https://graphql.anilist.co'
GRAPHQL_FILE_DIR = Path(__file__).parent.parent / 'graphql'


def load_query(name: str) -> str:
    """
    Load a GraphQL query from disk

    Args:
        name: The filename of the query file

    Returns: The query stored in the file
    """
    return load_file(GRAPHQL_FILE_DIR / name)


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

    def query(self, query: str, variables: Optional[dict] = None, is_file=True) -> dict:
        """
        Makes HTTP request to the Anilist API

        Args:
            query: The GraphQL query to POST to the API
            variables: variables for the query, can be None
            is_file: Wether the query is from a file

        Returns:
            The API response

        Raises:
            APIHTTPError if request failed
        """
        if is_file:
            query = load_query(query)
        post_json = {'query': query}
        if variables:
            post_json['variables'] = variables

        res = post(GRAPHQL_URL, json=post_json, headers=self.headers)
        try:
            res.raise_for_status()
        except HTTPError as e:
            raise APIError(res.status_code, str(e))
        else:
            return res.json()

    def query_pages(self, query: str, variables: dict, is_file=True) -> Iterable[dict]:
        """
        Make paged requests to the Anilist API

        Args:
            query: The GraphQL query to POST to the API
            variables: variables for the query, can be None
            is_file: Wether the query is from a file

        Returns:
            A generator yielding each page of the API response

        Raises:
            APIHTTPError if request failed
        """
        while True:
            res = self.query(query, variables, is_file)
            has_next = res['data']['Page']['pageInfo']['hasNextPage']
            yield res
            if not has_next:
                return
            variables['page'] += 1

    def get_season_animes(self, season: str, year: int, per_page: int,
                          sort: Optional[List[str]] = None) -> Iterable[dict]:
        """
        Query all anime of a given season

        Args:
            season: The season, one of: (WINTER, SPRING, SUMMER, FALL)
            year: The year for the season
            per_page: How many anime per page of the response
            sort: List of keys to sort by, defaults to ID. See
                https://anilist.github.io/ApiV2-GraphQL-Docs/mediasort.doc.html

        Returns:
            A generator yielding pages of anime in the season

        Raises:
            APIHTTPError if request failed
        """
        sort = sort or ['ID']
        variables = {
            'page': 1,
            'perPage': per_page,
            'season': season,
            'seasonYear': year,
            'sort': sort
        }
        return self.query_pages('season.graphql', variables)
