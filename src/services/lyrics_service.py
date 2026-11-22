import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dataclasses import replace

from infrastructure.api.lrclib_client import LRCLibClient
from infrastructure.api.netease_client import NetEaseClient
from models.lyrics import Lyrics
from models.song import Song

from utils.lrc_parser import parse_lrc


class LyricsService:

    def __init__(
        self,
        client: LRCLibClient | None = None,
        netease_client: NetEaseClient | None = None
    ):
        self.client = client or LRCLibClient()
        self.netease_client = netease_client or NetEaseClient()

    def _parse_response(
        self,
        response: dict | None,
        song: Song,
        source: str
    ) -> Lyrics | None:

        if not isinstance(response, dict):
            return None

        synced_lyrics = response.get("syncedLyrics")

        if not isinstance(synced_lyrics, str) or not synced_lyrics.strip():
            return None

        try:
            lyrics = parse_lrc(synced_lyrics, song)
            return replace(lyrics, source=source)

        except (ValueError, TypeError):
            return None

    def get_lyrics(self, song: Song) -> Lyrics:

        if not isinstance(song, Song):
            raise TypeError(
                "song debe ser una instancia de Song."
            )

        errors = []

        # 1. LRCLIB: búsqueda exacta
        try:
            response = self.client.search_lyrics(
                title=song.title,
                artist=song.artist,
                album=song.album,
                duration=song.duration
            )

            lyrics = self._parse_response(
                response,
                song,
                "LRCLIB"
            )

            if lyrics:
                return lyrics

        except Exception as error:
            errors.append(f"LRCLIB exacto: {error}")

        # 2. LRCLIB: búsqueda alternativa
        try:
            response = self.client.search_synced_lyrics(
                title=song.title,
                artist=song.artist
            )

            lyrics = self._parse_response(
                response,
                song,
                "LRCLIB"
            )

            if lyrics:
                return lyrics

        except Exception as error:
            errors.append(f"LRCLIB alternativo: {error}")

        # 3. NetEase
        try:
            response = self.netease_client.search_lyrics(
                title=song.title,
                artist=song.artist,
                duration=song.duration
            )

            lyrics = self._parse_response(
                response,
                song,
                "NetEase"
            )

            if lyrics:
                return lyrics

        except Exception as error:
            errors.append(f"NetEase: {error}")

        message = "No se encontraron letras sincronizadas válidas."

        if errors:
            message += "\n" + "\n".join(errors)

        raise LookupError(message)
