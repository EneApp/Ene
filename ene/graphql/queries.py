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

LIST_ANIME = """\
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
$licensed_by: [String],
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
            licensedBy_in: $licensed_by,
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
                startedAt{
                    year
                    month
                    day
                }
                completedAt {
                    year
                    month
                    day
                }
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

LIST_GENRES = 'query {GenreCollection}'

LIST_TAGS = """\
query {
    MediaTagCollection {
        id
        name
        category
        isAdult
        isGeneralSpoiler
        isMediaSpoiler
    }
}"""

FIND_ANIME = """\
query ($title: String) {
    Media(search: $title, type: ANIME) {
        id
        coverImage {
            large
             medium
        }
    }
}"""
