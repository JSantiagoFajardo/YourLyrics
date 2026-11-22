
import pytest

from controllers.lyrics_controller import LyricsController
from models.lyrics import Lyrics
from models.song import Song


class MockLyricsService:

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.received_song = None

    def get_lyrics(self, song):
        self.received_song = song

        if self.error:
            raise self.error

        return self.result


class MockLocalLyricsService:

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.received_path = None
        self.received_song = None

    def load_lrc_file(self, file_path, song=None):
        self.received_path = file_path
        self.received_song = song

        if self.error:
            raise self.error

        return self.result


@pytest.fixture
def song():
    return Song(title="My Song", artist="My Artist")


@pytest.fixture
def lyrics(song):
    from models.lyric_line import LyricLine

    return Lyrics(
        song=song,
        lines=(LyricLine(timestamp=10.0, text="First line"),),
        source="LRCLIB"
    )


def test_fetch_lyrics(song, lyrics):
    service = MockLyricsService(result=lyrics)
    controller = LyricsController(lyrics_service=service)

    result = controller.fetch_lyrics(song)

    assert result == lyrics
    assert controller.current_lyrics == lyrics
    assert service.received_song == song


def test_load_local_lyrics(song, lyrics, tmp_path):
    path = tmp_path / "song.lrc"

    service = MockLocalLyricsService(result=lyrics)
    controller = LyricsController(local_service=service)

    result = controller.load_local_lyrics(path, song)

    assert result == lyrics
    assert controller.current_lyrics == lyrics
    assert service.received_path == path
    assert service.received_song == song


def test_clear_lyrics(lyrics):
    service = MockLyricsService(result=lyrics)
    controller = LyricsController(lyrics_service=service)

    controller.fetch_lyrics(lyrics.song)
    controller.clear_lyrics()

    assert controller.current_lyrics is None


def test_current_lyrics_initially_empty():
    controller = LyricsController(
        lyrics_service=MockLyricsService(),
        local_service=MockLocalLyricsService()
    )

    assert controller.current_lyrics is None


def test_failed_fetch_does_not_replace_current_lyrics(song, lyrics):
    service = MockLyricsService(result=lyrics)
    controller = LyricsController(lyrics_service=service)

    controller.fetch_lyrics(song)

    service.error = ConnectionError("Connection failed")

    with pytest.raises(ConnectionError):
        controller.fetch_lyrics(song)

    assert controller.current_lyrics == lyrics


def test_failed_local_load_does_not_replace_current_lyrics(song, lyrics, tmp_path):
    service = MockLocalLyricsService(result=lyrics)
    controller = LyricsController(local_service=service)

    controller.load_local_lyrics(tmp_path / "song.lrc", song)

    service.error = FileNotFoundError("File not found")

    with pytest.raises(FileNotFoundError):
        controller.load_local_lyrics(tmp_path / "missing.lrc", song)

    assert controller.current_lyrics == lyrics
