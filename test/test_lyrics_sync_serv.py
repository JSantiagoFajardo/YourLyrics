
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from controllers.playback_controller import PlaybackController
from controllers.playback_message_handler import PlaybackMessageHandler
from infrastructure.api.websocket_server import WebSocketServer

from models.song import Song
from models.lyric_line import LyricLine
from models.lyrics import Lyrics
from services.lyrics_synchronization_service import LyricsSyncService


@pytest.fixture
def service():
    return LyricsSyncService()


@pytest.fixture
def lyrics():
    song = Song(
        title="Test Song",
        artist="Test Artist"
    )

    lines = (
        LyricLine(5.0, "First line"),
        LyricLine(10.0, "Second line"),
        LyricLine(15.0, "Third line"),
    )

    return Lyrics(song=song, lines=lines)


def test_get_first_line(service, lyrics):
    result = service.get_current_line(lyrics, 5.0)

    assert result.text == "First line"


def test_get_middle_line(service, lyrics):
    result = service.get_current_line(lyrics, 12.0)

    assert result.text == "Second line"


def test_get_last_line(service, lyrics):
    result = service.get_current_line(lyrics, 20.0)

    assert result.text == "Third line"


def test_before_first_line(service, lyrics):
    result = service.get_current_line(lyrics, 2.0)

    assert result is None


def test_exact_timestamp(service, lyrics):
    result = service.get_current_line(lyrics, 10.0)

    assert result.text == "Second line"


def test_reject_invalid_lyrics(service):
    with pytest.raises(TypeError):
        service.get_current_line("invalid", 10.0)


def test_reject_negative_position(service, lyrics):
    with pytest.raises(ValueError):
        service.get_current_line(lyrics, -1)


def test_reject_invalid_position(service, lyrics):
    with pytest.raises(TypeError):
        service.get_current_line(lyrics, "10")
