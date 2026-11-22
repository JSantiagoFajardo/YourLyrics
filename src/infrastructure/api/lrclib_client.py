
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class LRCLibClient:
    BASE_URL = "https://lrclib.net/api/get"
    TIMEOUT = 10

    def search_lyrics(
        self,
        title: str,
        artist: str,
        album: str | None = None,
        duration: float | None = None
    ) -> dict | None:

        params = {
            "track_name": title,
            "artist_name": artist,
        }

        if album:
            params["album_name"] = album

        if duration is not None:
            params["duration"] = duration

        url = f"{self.BASE_URL}?{urlencode(params)}"

        request = Request(
            url,
            headers={
                "User-Agent": "YourLyrics/0.1.0"
            }
        )

        try:
            with urlopen(request, timeout=self.TIMEOUT) as response:
                data = json.loads(response.read().decode("utf-8"))

                return data

        except HTTPError as error:
            if error.code == 404:
                return None

            raise

        except URLError as error:
            raise ConnectionError(
                f"No se pudo conectar con LRCLIB: {error}"
            ) from error
    
    def search_synced_lyrics(
        self,
        title: str,
        artist: str
    ) -> dict | None:

        params = {
            "track_name": title,
            "artist_name": artist,
        }

        url = f"https://lrclib.net/api/search?{urlencode(params)}"

        request = Request(
            url,
            headers={"User-Agent": "YourLyrics/0.1.0"}
        )

        try:
            with urlopen(request, timeout=self.TIMEOUT) as response:
                results = json.loads(response.read().decode("utf-8"))

            if not isinstance(results, list):
                return None

            for result in results:
                if isinstance(result, dict) and result.get("syncedLyrics"):
                    return result

            return None

        except HTTPError as error:
            if error.code == 404:
                return None
            raise

        except URLError as error:
            raise ConnectionError(
                f"No se pudo conectar con LRCLIB: {error}"
            ) from error