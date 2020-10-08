#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2020 Peijun Ma, Justin Sedge
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

import pytest
import requests
import responses

from ene.util import get_resource
from tests import CACHE_HOME, rmdir

IMAGE_URLS = [
    'https://cdn.anilist.co/img/dir/anime/reg/16049.jpg',
    'https://cdn.anilist.co/img/dir/anime/banner/16049.jpg'
]

with requests.get('https://httpbin.org/image/jpeg') as image_resp:
    MOCK_STATUS = image_resp.status_code
    MOCK_HEADERS = image_resp.headers
    MOCK_CONTENT = image_resp.content


@pytest.fixture()
def cache_dir():
    rmdir(CACHE_HOME, True)
    try:
        yield CACHE_HOME
    finally:
        rmdir(CACHE_HOME, True)


@pytest.fixture()
def mock_image_response():
    request_mock = responses.RequestsMock(assert_all_requests_are_fired=False)
    for url in IMAGE_URLS:
        request_mock.add(
            responses.GET,
            url,
            MOCK_CONTENT,
            headers=MOCK_HEADERS,
            status=MOCK_STATUS
        )
    yield request_mock


@pytest.mark.parametrize('url', IMAGE_URLS)
def test_get_resource_cache_miss(cache_dir, mock_image_response, url):
    expected = MOCK_CONTENT
    exp_path = Path(cache_dir, url.partition('anilist.co/')[-1])
    with mock_image_response:
        res = get_resource(url, cache_dir)
    assert res == exp_path
    assert res.is_file()
    with res.open('rb') as f:
        assert f.read() == expected


@pytest.mark.parametrize('url', IMAGE_URLS)
def test_get_resource_cache_hit(cache_dir, mock_image_response, url):
    expected = 'NullPointerException'
    exp_path = Path(cache_dir, url.partition('anilist.co/')[-1])
    exp_path.parent.mkdir(parents=True, exist_ok=True)
    exp_path.write_text(expected)
    with mock_image_response:
        res = get_resource(url, cache_dir)
    assert res == exp_path
    assert res.is_file()
    with res.open() as f:
        assert f.read() == expected
