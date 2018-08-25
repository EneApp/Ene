import ene.files
from . import HERE

from itertools import chain
import re
from tempfile import TemporaryDirectory
from pathlib import Path
import pytest

TEST_PATH = HERE / 'ene'


@pytest.fixture()
def mock_shows(directory):
    yield {
        'foo': [Path(directory / 'foo episode 1'),
                Path(directory / 'foo episode 2'),
                Path(directory / 'foo episode 3'),
                Path(directory / 'foo episode 4'),
                Path(directory / 'foo episode 5')],
        'bar': [Path(directory / 'bar episode 1'),
                Path(directory / 'bar episode 2'),
                Path(directory / 'bar episode 3')],
        'baz': [Path(directory / 'baz episode 1'),
                Path(directory / 'baz episode 2'),
                Path(directory / 'baz episode 3'),
                Path(directory / 'baz episode 4')]
    }


@pytest.fixture
def manager(directory) -> ene.files.FileManager:
    cfg = {'Local Paths': directory}
    files = ene.files.FileManager(cfg, Path(directory))
    yield files


@pytest.fixture()
def directory():
    with TemporaryDirectory() as path:
        for episode in chain.from_iterable(MOCK_SHOWS.values()):
            Path(path, episode).touch()
        yield path


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
                        Path('cat baz dog')]
    })
    assert set(res.keys()) == {'foo', 'bar', 'baz'}


def test_discover(manager, directory, mock_shows):
    # TODO: Actually compare something here properly
    manager.discover_episodes(directory)
    assert True