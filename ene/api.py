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

from typing import Optional

from requests import HTTPError, post

from .auth import OAuth
from .errors import APIError

CLIENT_ID = 584
GRAPHQL_URL = 'https://graphql.anilist.co'


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

    def _request(self, query: str, variables: Optional[dict] = None) -> dict:
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
        except HTTPError as e:
            raise APIError(res.status_code, str(e))
        else:
            return res.json()
