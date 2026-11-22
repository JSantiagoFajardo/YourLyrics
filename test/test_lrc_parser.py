
import pytest

from models.song import Song
from utils.lrc_parser import parse_lrc


def test_parse_lrc_with_metadata():
    content = """
    [ti:My Song]
    [ar:My Artist]
    [al:My Album]
    [00:12.50]First line
    [00:18.00]Second line
    """

    result = parse_lrc(content)

    assert result.song.title == "My Song"
    assert result.song.artist == "My Artist"
    assert result.song.album == "My Album"
    assert len(result.lines) == 2
    assert result.lines[0].text == "First line"
    assert result.lines[0].timestamp == 12.5


def test_parse_lrc_with_existing_song():
    song = Song(title="Song", artist="Artist")

    content = """
    [00:10.00]First line
    [00:20.00]Second line
    """

    result = parse_lrc(content, song)

    assert result.song == song
    assert len(result.lines) == 2


def test_parse_multiple_timestamps():
    content = """
    [ti:Song]
    [ar:Artist]
    [00:10.00][00:15.00]Same lyric
    """

    result = parse_lrc(content)

    assert len(result.lines) == 2
    assert result.lines[0].timestamp == 10.0
    assert result.lines[1].timestamp == 15.0
    assert result.lines[0].text == result.lines[1].text


def test_parse_sorts_lines():
    content = """
    [ti:Song]
    [ar:Artist]
    [00:30.00]Third
    [00:10.00]First
    [00:20.00]Second
    """

    result = parse_lrc(content)

    timestamps = [line.timestamp for line in result.lines]

    assert timestamps == [10.0, 20.0, 30.0]


def test_parse_without_required_metadata():
    content = "[00:10.00]Some lyric"

    with pytest.raises(ValueError):
        parse_lrc(content)


def test_parse_without_timed_lyrics():
    content = """
    [ti:Song]
    [ar:Artist]
    """

    with pytest.raises(ValueError):
        parse_lrc(content)


def test_parse_empty_content():
    with pytest.raises(ValueError):
        parse_lrc("")


def test_parse_invalid_content_type():
    with pytest.raises(TypeError):
        parse_lrc(None)


def test_parse_ignores_lines_without_timestamps():
    content = """
    [ti:Song]
    [ar:Artist]
    This line has no timestamp
    [00:10.00]Valid lyric
    """

    result = parse_lrc(content)

    assert len(result.lines) == 1
    assert result.lines[0].text == "Valid lyric"
