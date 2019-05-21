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
from itertools import repeat
from unittest.mock import MagicMock

import pytest
from option import Err, Ok
from requests import Session

from anilist.anilist_client import AnilistClient
from graphql.queries import LIST_ANIME
from tests.conftest import fake
from tests.domain.fake_faults import fake_fault


@pytest.fixture()
def mock_session():
    return MagicMock(Session)


def fake_media_page(media_per_page=2):
    return {
        'data': {
            'Page': {
                'media': [
                    fake_dict() for fake_dict in
                    repeat(fake.pydict, media_per_page)
                ]
            }
        }
    }


class TestListAnime:
    @pytest.mark.parametrize('expected', [
        [Ok(fake_media_page()), Ok(fake_media_page())],
        [Ok(fake_media_page()), Err(fake_fault())],
        [Err(fake_fault()), Ok(fake_media_page())],
        [Err(fake_fault()), Err(fake_fault())],
    ])
    def test_it_should_return_the_correct_pages(self, mock_session, expected):
        client = AnilistClient(mock_session, '')
        client.query_pages = MagicMock(return_value=expected)

        result = list(client.list_anime())

        assert len(result) == len(expected)
        for expected_page, actual_page in zip(expected, result):
            if expected_page.is_err:
                assert expected_page == actual_page
            else:
                assert ([data for data in
                         expected_page.unwrap()['data']['Page']['media']]
                        == [media.data for media in actual_page.unwrap()])

        client.query_pages.assert_called_once_with(LIST_ANIME, 20, None)
