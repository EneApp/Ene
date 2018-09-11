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
from typing import Dict, Iterable, List, Optional, Tuple

import attr
from requests import HTTPError, Session

from ene.constants import CLIENT_ID, GRAPHQL_URL
from ene.errors import APIError
from ene.util import dict_filter
from .auth import OAuth
from .enums import MediaFormat, MediaListStatus, MediaSeason, MediaSort, MediaStatus
from .types_ import FuzzyDate


@attr.s(slots=True)
class API:
    """
    Handles requests to the Anilist API
    """
    data_home = attr.ib()
    session = attr.ib(factory=Session, init=False)
    token = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.token = OAuth.get_token(self.data_home, CLIENT_ID, '127.0.0.1', 50000)
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

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
    ) -> Tuple[List[dict], bool]:
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

        Returns:
            The page anime returned and if there's a next page
        """
        query = """\
query (
$page: Int = 1,
$isAdult: Boolean = false,
$search: String,
$format: MediaFormat
$status: MediaStatus,
$season: MediaSeason,
$year: String,
$onList: Boolean,
$yearLesser: FuzzyDateInt,
$yearGreater: FuzzyDateInt,
$licensedBy: [String],
$includedGenres: [String],
$excludedGenres: [String],
$includedTags: [String],
$excludedTags: [String],
$sort: [MediaSort] = [SCORE_DESC, POPULARITY_DESC],
$perPage: Int,
) {
    Page (page: $page, perPage: $perPage) {
        pageInfo {
            total
            perPage
            currentPage
            lastPage
            hasNextPage
        }
        media (
            type: ANIME,
            season: $season,
            format: $format,
            status: $status,
            search: $search,
            onList: $onList,
            startDate_like: $year,
            startDate_lesser: $yearLesser,
            startDate_greater: $yearGreater,
            licensedBy_in: $licensedBy,
            genre_in: $includedGenres,
            genre_not_in: $excludedGenres,
            tag_in: $includedTags,
            tag_not_in: $excludedTags,
            sort: $sort,
            isAdult: $isAdult
        ) {
            id
            title {
                userPreferred
            }
            coverImage {
                large
            }
            bannerImage
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            season
            description
            type
            format
            status
            genres
            isAdult
            averageScore
            popularity
            mediaListEntry {
                id
                status
                score
                progress
                repeat
                private
                notes
                customLists
                startedAt
                completedAt
            }
            nextAiringEpisode {
                id
                airingAt
                episode
            }
            studios (isMain: true) {
                edges {
                    isMain
                    node {
                        id
                        name
                    }
                }
            }
        }
    }
}"""
        variables = dict_filter({
            'page': page,
            'isAdult': is_adult,
            'search': search,
            'format': format_.name if format_ else None,
            'status': status.name if status else None,
            'season': season.name if season else None,
            'onList': on_list,
            'licensedBy': licensed_by,
            'includedGenres': included_genres,
            'excludedGenres': excluded_genres,
            'includedTags': included_tags,
            'excludedTags': excluded_tags,
        })
        if sort:
            variables['sort'] = [s.name for s in sort]
        if year_range and year_range[0] and year_range[1]:
            start, fin = year_range
            if start == fin:
                variables['year'] = f'{start}%'
            else:
                variables['yearGreater'] = start * 10000
                variables['yearLesser'] = fin * 10000
        res = self.query(query, variables).get('data', {}).get('Page', {})
        has_next = res.get('pageInfo', {}).get('hasNextPage', False)
        return res.get('media', []), has_next

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

    def get_show(self, show):
        """
        Gets information about a single show by name

        Args:
            show:
                The show to look up

        Returns:
            Information about the show
        """
        query = """\
        query ($title: String) {
            Media(search: $title, type: ANIME) {
                id
                coverImage {
                    large
                     medium
                }
            }
        }"""
        variables = {
            'title': show
        }
        res = self.query(query, variables)
        return res

    def update_media_list_entry(  # pylint: disable=R0913
            self,
            media_id: int,
            status: Optional[MediaListStatus] = None,
            score: Optional[float] = None,
            progress: Optional[int] = None,
            repeat: Optional[int] = None,
            private: Optional[bool] = None,
            notes: Optional[str] = None,
            custom_lists: Optional[Dict[str, bool]] = None,
            started_at: Optional[FuzzyDate] = None,
            completed_at: Optional[FuzzyDate] = None,
    ) -> Optional[dict]:
        """
        Update a media list entry for the user.

        Args:
            media_id: The media ID
            status: The watching status
            score: The score of the entry
            progress: The amount of episodes consumed by the user
            custom_lists: Map of booleans for which lists the entry are in
            private: If the entry should only be visible to authenticated user
            notes: Text notes
            started_at: When the entry was started by the user
            completed_at: When the entry was completed by the user
            repeat: The amount of times the user has re-watched the media

        Returns:
            The updated media entry values.
        """
        query = """\
mutation (
    $mediaId: Int,
    $status: MediaListStatus,
    $score: Float,
    $progress: Int,
    $customLists: Json,
    $private: Boolean,
    $notes: String,
    $startedAt: FuzzyDate,
    $completedAt: FuzzyDate,
    $repeat: Int
) {
    SaveMediaListEntry (
        mediaId: $mediaId,
        status: $status,
        score: $score,
        progress: $progress,
        customLists: $customLists,
        private: $private,
        notes: $notes,
        startedAt: $startedAt,
        completedAt: $completedAt,
        repeat: $repeat
    ) {
            id
            status
            score
            progress
            repeat
            private
            notes
            customLists
            startedAt
            completedAt
    }
}"""
        variables = dict_filter({
            "mediaId": media_id,
            "status": status.name if status else None,
            "score": score,
            "progress": progress,
            "customLists": custom_lists,
            "private": private,
            "notes": notes,
            "startedAt": {
                "year": started_at.year,
                "month": started_at.month,
                "day": started_at.day
            } if started_at else None,
            "completedAt": {
                "year": completed_at.year,
                "month": completed_at.month,
                "day": completed_at.day
            } if completed_at else None,
            "repeat": repeat,
        })
        return self.query(query, variables)
