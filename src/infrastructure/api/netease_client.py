
import json
import re
import unicodedata

from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class NetEaseClient:
    BASE_URL = "https://music.163.com"
    TIMEOUT = 10

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://music.163.com/",
    }

    @staticmethod
    def _normalize(value: str) -> str:
        value = unicodedata.normalize("NFKD", value or "")
        value = "".join(
            char for char in value
            if not unicodedata.combining(char)
        )
        value = value.lower()
        return re.sub(r"[^a-z0-9]", "", value)

    def _request(self, endpoint: str, params: dict) -> dict | None:
        url = f"{self.BASE_URL}{endpoint}?{urlencode(params)}"

        request = Request(url, headers=self.HEADERS)

        try:
            with urlopen(request, timeout=self.TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))

            return data if isinstance(data, dict) else None

        except HTTPError as error:
            if error.code == 404:
                return None

            raise ConnectionError(
                f"Error HTTP de NetEase: {error.code}"
            ) from error

        except URLError as error:
            raise ConnectionError(
                f"No se pudo conectar con NetEase: {error}"
            ) from error

        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError(
                "NetEase devolvió una respuesta inválida."
            ) from error

    def search_lyrics(
        self,
        title: str,
        artist: str,
        duration: float | None = None
    ) -> dict | None:

        data = self._request(
            "/api/search/get",
            {
                "s": f"{title} {artist}",
                "type": 1,
                "limit": 10,
                "offset": 0,
            }
        )

        if not data:
            return None

        songs = data.get("result", {}).get("songs", [])

        if not isinstance(songs, list):
            return None

        target_title = self._normalize(title)
        target_artist = self._normalize(artist)

        candidates = []

        for song in songs:
            if not isinstance(song, dict):
                continue

            song_name = self._normalize(song.get("name", ""))

            artists = song.get("artists") or song.get("ar") or []
            artist_names = [
                self._normalize(item.get("name", ""))
                for item in artists
                if isinstance(item, dict)
            ]

            if not song_name or not artist_names:
                continue

            title_match = (
                song_name == target_title
                or target_title in song_name
                or song_name in target_title
            )

            artist_match = any(
                target_artist == name
                or target_artist in name
                or name in target_artist
                for name in artist_names
                if name
            )

            if not title_match or not artist_match:
                continue

            score = 0

            if song_name == target_title:
                score += 2
            else:
                score += 1

            if target_artist in artist_names:
                score += 2
            else:
                score += 1

            if duration is not None:
                song_duration = song.get("duration")

                if song_duration is not None:
                    difference = abs(
                        float(song_duration) / 1000 - duration
                    )

                    if difference > 15:
                        continue

                    if difference <= 5:
                        score += 2
                    else:
                        score += 1

            candidates.append((score, song))

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: item[0],
            reverse=True
        )

        song_id = candidates[0][1].get("id")

        if song_id is None:
            return None

        lyric_data = self._request(
            "/api/song/lyric",
            {
                "id": song_id,
                "lv": 1,
                "tv": 0,
            }
        )

        if not lyric_data:
            return None

        lrc = lyric_data.get("lrc", {})
        synced_lyrics = lrc.get("lyric") if isinstance(lrc, dict) else None

        if not synced_lyrics:
            return None

        return {
            "syncedLyrics": synced_lyrics,
            "source": "NetEase",
            "song_id": song_id,
        }
