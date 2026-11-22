
from pathlib import Path

from models.lyrics import Lyrics
from models.song import Song
from services.lyrics_service import LyricsService
from services.local_lyrics_service import LocalLyricsService


class LyricsController:

    def __init__(
        self,
        lyrics_service: LyricsService | None = None,
        local_service: LocalLyricsService | None = None
    ):
        self.lyrics_service = lyrics_service or LyricsService()
        self.local_service = local_service or LocalLyricsService()

        self._current_lyrics: Lyrics | None = None

    @property
    def current_lyrics(self) -> Lyrics | None:
        return self._current_lyrics

    def fetch_lyrics(self, song: Song) -> Lyrics:
        lyrics = self.lyrics_service.get_lyrics(song)

        self._current_lyrics = lyrics

        return lyrics

    def load_local_lyrics(
        self,
        file_path: str | Path,
        song: Song | None = None
    ) -> Lyrics:
        lyrics = self.local_service.load_lrc_file(file_path, song)

        self._current_lyrics = lyrics

        return lyrics

    def clear_lyrics(self) -> None:
        self._current_lyrics = None

        
    def set_lyrics(self, lyrics: Lyrics) -> None:
        if not isinstance(lyrics, Lyrics):
            raise TypeError("lyrics debe ser una instancia de Lyrics.")

        self._current_lyrics = lyrics