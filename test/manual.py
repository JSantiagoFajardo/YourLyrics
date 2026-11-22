import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models.song import Song
from models.lyric_line import LyricLine
from models.lyrics import Lyrics
from models.playback import Playback


song = Song(
    title="Bohemian Rhapsody",
    artist="Queen",
    duration=354
)

lines = (
    LyricLine(12.5, "Is this the real life?"),
    LyricLine(16.2, "Is this just fantasy?"),
    LyricLine(20.1, "Caught in a landslide")
)

lyrics = Lyrics(
    song=song,
    lines=lines,
    synced=True,
    source="LRCLIB"
)

playback = Playback(
    song=song,
    position=16.5,
    is_playing=True
)

print(song)
print(lyrics)
print(playback)



