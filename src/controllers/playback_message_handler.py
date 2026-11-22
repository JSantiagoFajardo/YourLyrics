
import math

from controllers.playback_controller import PlaybackController
from models.song import Song


class PlaybackMessageHandler:

    def __init__(self, playback_controller: PlaybackController):
        self.playback_controller = playback_controller
        self._last_track_id = None
        self._position_offset = 0.0

    def handle_message(self, data: dict):

        if not isinstance(data, dict):
            raise TypeError("El mensaje debe ser un diccionario.")

        if data.get("type") != "playback_update":
            raise ValueError("Tipo de mensaje no soportado.")

        position = self._validate_number(data.get("position"), "position")

        is_playing = data.get("is_playing")
        is_paused = data.get("is_paused")

        if not isinstance(is_playing, bool):
            raise TypeError("is_playing debe ser booleano.")

        if not isinstance(is_paused, bool):
            raise TypeError("is_paused debe ser booleano.")

        song = self._build_song(data)

        if song is None:
            return None

        track_id = data.get("track_id")

        if not isinstance(track_id, str):
            track_id = f"{song.artist}::{song.title}"

        if track_id != self._last_track_id:
            self._last_track_id = track_id
            self._position_offset = position

            print(
                f"[YourLyrics] Nueva canción: {track_id} "
                f"| Posición inicial: {position:.2f}"
            )

        relative_position = max(0.0, position - self._position_offset)

        return self.playback_controller.update_playback(
            song=song,
            position=relative_position,
            is_playing=is_playing,
            is_paused=is_paused
        )

    def _build_song(self, data: dict) -> Song | None:
        title = data.get("title")
        artist = data.get("artist")

        if title is None and artist is None:
            return None

        if not isinstance(title, str) or not isinstance(artist, str):
            raise TypeError("title y artist deben ser cadenas de texto.")

        album = data.get("album")
        duration = data.get("duration")
        source_id = data.get("source_id")

        if album is not None and not isinstance(album, str):
            raise TypeError("album debe ser una cadena de texto.")

        if source_id is not None and not isinstance(source_id, str):
            raise TypeError("source_id debe ser una cadena de texto.")

        if duration is not None:
            duration = self._validate_number(duration, "duration")

        return Song(
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            source_id=source_id
        )

    @staticmethod
    def _validate_number(value, field: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{field} debe ser un número.")

        if not math.isfinite(value) or value < 0:
            raise ValueError(
                f"{field} debe ser un número válido no negativo."
            )

        return float(value)
