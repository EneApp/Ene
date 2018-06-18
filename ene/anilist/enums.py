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

"""This file is generated by a tool, see tools/make_enums.py"""

from enum import Enum, auto


class ActivitySort(Enum):
    ID = auto()
    ID_DESC = auto()


class ActivityType(Enum):
    TEXT = auto()
    ANIME_LIST = auto()
    MANGA_LIST = auto()
    MESSAGE = auto()
    MEDIA_LIST = auto()


class AiringSort(Enum):
    ID = auto()
    ID_DESC = auto()
    MEDIA_ID = auto()
    MEDIA_ID_DESC = auto()
    TIME = auto()
    TIME_DESC = auto()
    EPISODE = auto()
    EPISODE_DESC = auto()


class CharacterRole(Enum):
    MAIN = auto()
    SUPPORTING = auto()
    BACKGROUND = auto()


class CharacterSort(Enum):
    ID = auto()
    ID_DESC = auto()
    ROLE = auto()
    ROLE_DESC = auto()
    SEARCH_MATCH = auto()
    FAVOURITES = auto()
    FAVOURITES_DESC = auto()


class LikeableType(Enum):
    THREAD = auto()
    THREAD_COMMENT = auto()
    ACTIVITY = auto()
    ACTIVITY_REPLY = auto()


class MediaFormat(Enum):
    TV = auto()
    TV_SHORT = auto()
    MOVIE = auto()
    SPECIAL = auto()
    OVA = auto()
    ONA = auto()
    MUSIC = auto()
    MANGA = auto()
    NOVEL = auto()
    ONE_SHOT = auto()


class MediaListSort(Enum):
    MEDIA_ID = auto()
    MEDIA_ID_DESC = auto()
    SCORE = auto()
    SCORE_DESC = auto()
    STATUS = auto()
    STATUS_DESC = auto()
    PROGRESS = auto()
    PROGRESS_DESC = auto()
    PROGRESS_VOLUMES = auto()
    PROGRESS_VOLUMES_DESC = auto()
    REPEAT = auto()
    REPEAT_DESC = auto()
    PRIORITY = auto()
    PRIORITY_DESC = auto()
    STARTED_ON = auto()
    STARTED_ON_DESC = auto()
    FINISHED_ON = auto()
    FINISHED_ON_DESC = auto()
    ADDED_TIME = auto()
    ADDED_TIME_DESC = auto()
    UPDATED_TIME = auto()
    UPDATED_TIME_DESC = auto()


class MediaListStatus(Enum):
    CURRENT = auto()
    PLANNING = auto()
    COMPLETED = auto()
    DROPPED = auto()
    PAUSED = auto()
    REPEATING = auto()


class MediaRankType(Enum):
    RATED = auto()
    POPULAR = auto()


class MediaRelation(Enum):
    ADAPTATION = auto()
    PREQUEL = auto()
    SEQUEL = auto()
    PARENT = auto()
    SIDE_STORY = auto()
    CHARACTER = auto()
    SUMMARY = auto()
    ALTERNATIVE = auto()
    SPIN_OFF = auto()
    OTHER = auto()


class MediaSeason(Enum):
    WINTER = auto()
    SPRING = auto()
    SUMMER = auto()
    FALL = auto()


class MediaSort(Enum):
    ID = auto()
    ID_DESC = auto()
    TITLE_ROMAJI = auto()
    TITLE_ROMAJI_DESC = auto()
    TITLE_ENGLISH = auto()
    TITLE_ENGLISH_DESC = auto()
    TITLE_NATIVE = auto()
    TITLE_NATIVE_DESC = auto()
    TYPE = auto()
    TYPE_DESC = auto()
    FORMAT = auto()
    FORMAT_DESC = auto()
    START_DATE = auto()
    START_DATE_DESC = auto()
    END_DATE = auto()
    END_DATE_DESC = auto()
    SCORE = auto()
    SCORE_DESC = auto()
    POPULARITY = auto()
    POPULARITY_DESC = auto()
    TRENDING = auto()
    TRENDING_DESC = auto()
    EPISODES = auto()
    EPISODES_DESC = auto()
    DURATION = auto()
    DURATION_DESC = auto()
    STATUS = auto()
    STATUS_DESC = auto()
    CHAPTERS = auto()
    CHAPTERS_DESC = auto()
    VOLUMES = auto()
    VOLUMES_DESC = auto()
    UPDATED_AT = auto()
    UPDATED_AT_DESC = auto()
    SEARCH_MATCH = auto()
    FAVOURITES = auto()
    FAVOURITES_DESC = auto()


class MediaSource(Enum):
    ORIGINAL = auto()
    MANGA = auto()
    LIGHT_NOVEL = auto()
    VISUAL_NOVEL = auto()
    VIDEO_GAME = auto()
    OTHER = auto()


class MediaStatus(Enum):
    FINISHED = auto()
    RELEASING = auto()
    NOT_YET_RELEASED = auto()
    CANCELLED = auto()


class MediaTrendSort(Enum):
    ID = auto()
    ID_DESC = auto()
    MEDIA_ID = auto()
    MEDIA_ID_DESC = auto()
    DATE = auto()
    DATE_DESC = auto()
    SCORE = auto()
    SCORE_DESC = auto()
    POPULARITY = auto()
    POPULARITY_DESC = auto()
    TRENDING = auto()
    TRENDING_DESC = auto()
    EPISODE = auto()
    EPISODE_DESC = auto()


class MediaType(Enum):
    ANIME = auto()
    MANGA = auto()


class NotificationType(Enum):
    ACTIVITY_MESSAGE = auto()
    ACTIVITY_REPLY = auto()
    FOLLOWING = auto()
    ACTIVITY_MENTION = auto()
    THREAD_COMMENT_MENTION = auto()
    THREAD_SUBSCRIBED = auto()
    THREAD_COMMENT_REPLY = auto()
    AIRING = auto()
    ACTIVITY_LIKE = auto()
    ACTIVITY_REPLY_LIKE = auto()
    THREAD_LIKE = auto()
    THREAD_COMMENT_LIKE = auto()


class ReviewRating(Enum):
    NO_VOTE = auto()
    UP_VOTE = auto()
    DOWN_VOTE = auto()


class ReviewSort(Enum):
    ID = auto()
    ID_DESC = auto()
    SCORE = auto()
    SCORE_DESC = auto()
    RATING = auto()
    RATING_DESC = auto()
    CREATED_AT = auto()
    CREATED_AT_DESC = auto()
    UPDATED_AT = auto()
    UPDATED_AT_DESC = auto()


class ScoreFormat(Enum):
    POINT_100 = auto()
    POINT_10_DECIMAL = auto()
    POINT_10 = auto()
    POINT_5 = auto()
    POINT_3 = auto()


class StaffLanguage(Enum):
    JAPANESE = auto()
    ENGLISH = auto()
    KOREAN = auto()
    ITALIAN = auto()
    SPANISH = auto()
    PORTUGUESE = auto()
    FRENCH = auto()
    GERMAN = auto()
    HEBREW = auto()
    HUNGARIAN = auto()


class StaffSort(Enum):
    ID = auto()
    ID_DESC = auto()
    ROLE = auto()
    ROLE_DESC = auto()
    LANGUAGE = auto()
    LANGUAGE_DESC = auto()
    SEARCH_MATCH = auto()
    FAVOURITES = auto()
    FAVOURITES_DESC = auto()


class StudioSort(Enum):
    ID = auto()
    ID_DESC = auto()
    NAME = auto()
    NAME_DESC = auto()
    SEARCH_MATCH = auto()
    FAVOURITES = auto()
    FAVOURITES_DESC = auto()


class ThreadSort(Enum):
    ID = auto()
    ID_DESC = auto()
    TITLE = auto()
    TITLE_DESC = auto()
    CREATED_AT = auto()
    CREATED_AT_DESC = auto()
    UPDATED_AT = auto()
    UPDATED_AT_DESC = auto()
    REPLIED_AT = auto()
    REPLIED_AT_DESC = auto()
    REPLY_COUNT = auto()
    REPLY_COUNT_DESC = auto()
    VIEW_COUNT = auto()
    VIEW_COUNT_DESC = auto()
    IS_STICKY = auto()
    SEARCH_MATCH = auto()


class UserSort(Enum):
    ID = auto()
    ID_DESC = auto()
    USERNAME = auto()
    USERNAME_DESC = auto()
    WATCHED_TIME = auto()
    WATCHED_TIME_DESC = auto()
    CHAPTERS_READ = auto()
    CHAPTERS_READ_DESC = auto()
    SEARCH_MATCH = auto()


class UserTitleLanguage(Enum):
    ROMAJI = auto()
    ENGLISH = auto()
    NATIVE = auto()
    ROMAJI_STYLISED = auto()
    ENGLISH_STYLISED = auto()
    NATIVE_STYLISED = auto()
