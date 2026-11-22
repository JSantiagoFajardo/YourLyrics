import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import io
import json
from urllib.error import HTTPError, URLError

import pytest

from src.infrastructure.api.lrclib_client import LRCLibClient


def test_search_lyrics_success(monkeypatch):
    expected_data = {
        "id": 123,
        "trackName": "My Song",
        "artistName": "My Artist",
        "syncedLyrics": "[00:10.00]First line"
    }

    def mock_urlopen(request, timeout):
        response = {
            "status": 200,
            "data": expected_data
        }

        return io.BytesIO(json.dumps(response["data"]).encode("utf-8"))

    monkeypatch.setattr(
        "src.infrastructure.api.lrclib_client.urlopen",
        mock_urlopen
    )

    client = LRCLibClient()

    result = client.search_lyrics("My Song", "My Artist")

    assert result == expected_data


def test_search_lyrics_not_found(monkeypatch):
    def mock_urlopen(request, timeout):
        raise HTTPError(
            url=request.full_url,
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None
        )

    monkeypatch.setattr(
        "src.infrastructure.api.lrclib_client.urlopen",
        mock_urlopen
    )

    client = LRCLibClient()

    result = client.search_lyrics("Unknown Song", "Unknown Artist")

    assert result is None


def test_search_lyrics_connection_error(monkeypatch):
    def mock_urlopen(request, timeout):
        raise URLError("Connection failed")

    monkeypatch.setattr(
        "src.infrastructure.api.lrclib_client.urlopen",
        mock_urlopen
    )

    client = LRCLibClient()

    with pytest.raises(ConnectionError):
        client.search_lyrics("My Song", "My Artist")


def test_search_lyrics_with_optional_parameters(monkeypatch):
    captured_request = {}

    def mock_urlopen(request, timeout):
        captured_request["url"] = request.full_url
        captured_request["timeout"] = timeout

        return io.BytesIO(b'{"id": 123}')

    monkeypatch.setattr(
        "src.infrastructure.api.lrclib_client.urlopen",
        mock_urlopen
    )

    client = LRCLibClient()

    client.search_lyrics(
        title="My Song",
        artist="My Artist",
        album="My Album",
        duration=180
    )

    assert "album_name=My+Album" in captured_request["url"]
    assert "duration=180" in captured_request["url"]
    assert captured_request["timeout"] == 10
