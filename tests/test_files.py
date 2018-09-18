import ene.files
from . import HERE

from itertools import chain
import re
from tempfile import TemporaryDirectory
from pathlib import Path
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
              'adventures of baz ep1.mp4',
              'adventures of baz ep2.mp4',
              'adventures of baz ep3.mp4',
              'adventures of baz ep4.mp4'
              ]


@pytest.fixture()
def mock_shows(directory):
    yield {
        'isekai foo': [directory / 'isekai foo e1.mkv',
                       directory / 'isekai foo e2.mkv',
                       directory / 'isekai foo e3.mkv',
                       directory / 'isekai foo e4.mkv',
                       directory / 'isekai foo e5.mkv'],
        'bar quest': [directory / 'bar quest 01.avi',
                      directory / 'bar quest 02.avi',
                      directory / 'bar quest 03.avi'],
        'adventures of baz': [directory / 'adventures of baz ep1.mp4',
                              directory / 'adventures of baz ep2.mp4',
                              directory / 'adventures of baz ep3.mp4',
                              directory / 'adventures of baz ep4.mp4']
    }


@pytest.fixture
def manager(directory) -> ene.files.FileManager:
    cfg = {'Local Paths': [directory]}
    files = ene.files.FileManager(cfg, Path(directory))
    yield files


@pytest.fixture()
def directory():
    with TemporaryDirectory() as path:
        for episode in MOCK_FILES:
            Path(path, episode).touch()
        yield Path(path)


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
    manager.refresh_shows()
    for show in mock_shows:
        assert set(mock_shows[show]) == set(manager.series[show])


def test_find(manager, mock_shows):
    for show in mock_shows:
        manager.refresh_single_show(show)
        assert mock_shows[show] == manager.series[show]

