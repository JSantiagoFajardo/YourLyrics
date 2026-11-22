
import pytest

from models.song import Song
from models.lyrics import Lyrics
from services.lyrics_service import LyricsService


class MockLRCLibClient:

    def __init__(self, response):
        self.response = response
        self.last_params = None

    def search_lyrics(self, **kwargs):
        self.last_params = kwargs
        return self.response


@pytest.fixture
def song():
    return Song(
        title="My Song",
        artist="My Artist",
        album="My Album",
        duration=180
    )


def test_get_lyrics_success(song):
    response = {
        "syncedLyrics": (
            "[00:10.00]First line\n"
            "[00:20.00]Second line"
        )
    }

    client = MockLRCLibClient(response)
    service = LyricsService(client)

    result = service.get_lyrics(song)

    assert isinstance(result, Lyrics)
    assert result.song == song
    assert len(result.lines) == 2
    assert result.source == "LRCLIB"
    assert result.synced is True


def test_get_lyrics_not_found(song):
    client = MockLRCLibClient(None)
    service = LyricsService(client)

    with pytest.raises(LookupError):
        service.get_lyrics(song)


def test_get_lyrics_without_synced_lyrics(song):
    response = {
        "syncedLyrics": None,
        "plainLyrics": "Some unsynchronized lyrics"
    }

    client = MockLRCLibClient(response)
    service = LyricsService(client)

    with pytest.raises(LookupError):
        service.get_lyrics(song)


def test_get_lyrics_invalid_response(song):
    client = MockLRCLibClient("invalid response")
    service = LyricsService(client)

    with pytest.raises(ValueError):
        service.get_lyrics(song)


def test_get_lyrics_receives_song_information(song):
    client = MockLRCLibClient({
        "syncedLyrics": "[00:10.00]First line"
    })

    service = LyricsService(client)
    service.get_lyrics(song)

    assert client.last_params == {
        "title": "My Song",
        "artist": "My Artist",
        "album": "My Album",
        "duration": 180
    }


def test_get_lyrics_invalid_song():
    service = LyricsService(MockLRCLibClient(None))

    with pytest.raises(TypeError):
        service.get_lyrics("My Song")
