import ene.files
from . import HERE

import re
import pytest

TEST_PATH = HERE / 'ene'
MOCK_FILES = ['isekai foo e1.mkv',
              'isekai foo e2.mkv',
              'isekai foo e3.mkv',
              'isekai foo e4.mkv',
              'isekai foo e5.mkv',
              'bar quest 01.avi',
              'bar quest 02.avi',
              'bar quest 03.avi',
              'bar quest OP1.avi',
              'adventures of baz ep1.mp4',
              'adventures of baz ep2.mp4',
              'adventures of baz ep3.mp4',
              'adventures of baz ep4.mp4',
              'information.txt'
              ]


@pytest.fixture()
def mock_shows():
    yield {
        'isekai foo': [TEST_PATH / 'isekai foo e1.mkv',
                       TEST_PATH / 'isekai foo e2.mkv',
                       TEST_PATH / 'isekai foo e3.mkv',
                       TEST_PATH / 'isekai foo e4.mkv',
                       TEST_PATH / 'isekai foo e5.mkv'],
        'bar quest': [TEST_PATH / 'bar quest 01.avi',
                      TEST_PATH / 'bar quest 02.avi',
                      TEST_PATH / 'bar quest 03.avi'],
        'adventures of baz': [TEST_PATH / 'adventures of baz ep1.mp4',
                              TEST_PATH / 'adventures of baz ep2.mp4',
                              TEST_PATH / 'adventures of baz ep3.mp4',
                              TEST_PATH / 'adventures of baz ep4.mp4']
    }


@pytest.fixture
def manager() -> ene.files.FileManager:
    cfg = {'Local Paths': [TEST_PATH]}
    files = ene.files.FileManager(cfg)
    yield files


def test_regex():
    expected = re.compile(r'.*foo.*bar.*')
    actual = ene.files._build_regex('foo bar')
    assert actual == expected


def test_clean_titles():
    test_titles = ['[Bar] foo',
                   '(Bar) foo',
                   '01. foo',
                   'foo e1',
                   'foo s1e3',
                   'foo - 4 - bar',
                   ' foo ']
    for title in test_titles:
        assert ene.files.clean_title(title) == 'foo'
    assert ene.files.clean_title('foo s2') == 'foo Season 2'


def test_discover(manager, mock_shows):
    manager.discover_episodes(TEST_PATH, MOCK_FILES)
    for show in mock_shows:
        assert set(mock_shows[show]) == set([x.path for x in manager.series[show].episodes])


def test_find(manager, mock_shows):
    for show in mock_shows:
        assert mock_shows[show] == [x.path for x in manager.find_episodes(show, mock_shows[show])]

