import ene.files
from . import HERE

from itertools import chain
import re
from tempfile import TemporaryDirectory
from pathlib import Path
import pytest

TEST_PATH = HERE / 'ene'
MOCK_FILES = ['foo e1.avi',
              'foo e2.avi',
              'foo e3.avi',
              'foo e4.avi',
              'foo e5.avi',
              'bar 01.mkv',
              'bar 02.mkv',
              'bar 03.mkv',
              'baz ep1.mp4',
              'baz ep2.mp4',
              'baz ep3.mp4',
              'baz ep4.mp4'
              ]


@pytest.fixture()
def mock_shows(directory):
    yield {
        'foo': [directory / 'foo e1.avi',
                directory / 'foo e2.avi',
                directory / 'foo e3.avi',
                directory / 'foo e4.avi',
                directory / 'foo e5.avi'],
        'bar': [directory / 'bar 01.mkv',
                directory / 'bar 02.mkv',
                directory / 'bar 03.mkv'],
        'baz': [directory / 'baz ep1.mp4',
                directory / 'baz ep2.mp4',
                directory / 'baz ep3.mp4',
                directory / 'baz ep4.mp4']
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
    res = ene.files.clean_titles({
        '[foo] foo[1080p].mkv': [],
        '[bar] bar - 01.mp4': [],
        '[baz] bar - 02 [720p].wav': [],
        'foo bar baz': [Path('foo bar baz'),
                        Path('cat baz dog')],
        '[Foobar the Film]': []
    })
    assert set(res.keys()) == {'foo', 'bar', 'baz', '[Foobar the Film]'}


def test_discover(manager, mock_shows):
    manager.refresh_shows()
    for show in mock_shows:
        assert mock_shows[show] == manager.series[show]


def test_find(manager, mock_shows):
    for show in mock_shows:
        manager.refresh_single_show(show)
        assert mock_shows[show] == manager.series[show]

