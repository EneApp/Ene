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

from typing import Iterable, List, Optional

import attr
from option import Err, Ok, Result
from requests import HTTPError, Session

from domain.faults import Faults, HTTPFault
from graphql.filters import ListAnimeFilter
from graphql.inputs import UpdateMediaListEntryInput
from graphql.mutations import UPDATE_MEDIA_LIST_ENTRY
from graphql.queries import FIND_ANIME, LIST_ANIME, LIST_GENRES
from graphql.schema.media import Media

ApiResult = Result[dict, Faults]


@attr.s(auto_attribs=True)
class AnilistClient:
    session: Session
    graphql_endpoint: str

    def list_anime(
            self,
            per_page: int = 20,
            list_anime_filter: ListAnimeFilter = None
    ) -> Iterable[Result[List[Media], Faults]]:
        for page in self.query_pages(
                LIST_ANIME,
                per_page,
                list_anime_filter.data if list_anime_filter else None
        ):
            yield page.map(_process_media_page)

    def list_genres(self) -> Result[List[str], Faults]:
        return self.query(LIST_GENRES).map(
            lambda res: res.get('data', {}).get('GenreCollection', [])
        )

    def find_anime(self, title: str) -> Result[Media, Faults]:
        return self.query(FIND_ANIME, {'title': title}).map(
            lambda show: Media(show.get('data', {}).get('Media', {}))
        )

    def update_media_list_entry(
            self, media_list_entry_input: UpdateMediaListEntryInput
    ) -> ApiResult:
        return self.query(UPDATE_MEDIA_LIST_ENTRY, media_list_entry_input.data)

    def query(self, query: str, variables: Optional[dict] = None) -> ApiResult:
        post_body = ({'query': query, 'variables': variables}
                     if variables else {'query': query})
        post_result = self.session.post(self.graphql_endpoint, json=post_body)

        try:
            result_json = post_result.json()
        except ValueError:
            result_json = None

        try:
            post_result.raise_for_status()
        except HTTPError as http_error:
            errors = (result_json or {}).get('errors', []) + [str(http_error)]
            return Err(HTTPFault(post_result.status_code, ', '.join(errors)).to_faults())
        else:
            return Ok(result_json)

    def query_pages(
            self, query: str, per_page: int, variables: Optional[dict] = None
    ) -> Iterable[ApiResult]:
        variables = dict(page=1, perPage=per_page, **(variables or {}))

        has_next_page = True
        while has_next_page:
            page_result = self.query(query, variables)
            has_next_page = page_result.map(_has_next_page).unwrap_or(False)
            yield page_result
            variables['page'] += 1


def _process_media_page(page: dict) -> List[Media]:
    return [
        Media(media) for media in page.get('data', {}).get('Page', {}).get('media', [])
    ]


def _has_next_page(page_result: dict) -> bool:
    return (page_result
            .get('data', {})
            .get('Page', {})
            .get('pageInfo', {})
            .get('hasNextPage', False))
