
from bisect import bisect_right
from math import isfinite

from models.lyrics import Lyrics


class LyricsSyncService:

    def get_current_line(self, lyrics, position):
        self._validate_position(lyrics, position)

        if not lyrics.lines:
            return None

        timestamps = [line.timestamp for line in lyrics.lines]
        index = bisect_right(timestamps, position) - 1

        return lyrics.lines[index] if index >= 0 else None

    def get_next_line(self, lyrics, position):
        self._validate_position(lyrics, position)

        if not lyrics.lines:
            return None

        timestamps = [line.timestamp for line in lyrics.lines]
        index = bisect_right(timestamps, position)

        return lyrics.lines[index] if index < len(lyrics.lines) else None

    def _validate_position(self, lyrics, position):
        if not isinstance(lyrics, Lyrics):
            raise TypeError("lyrics debe ser una instancia de Lyrics.")

        if isinstance(position, bool) or not isinstance(position, (int, float)):
            raise TypeError("position debe ser un número.")

        if not isfinite(position) or position < 0:
            raise ValueError("position debe ser un número finito no negativo.")

    def is_instrumental_break(
        self, lyrics, position, gap_threshold=8.5, start_delay=6.2
    ):
        self._validate_position(lyrics, position)

        for index, line in enumerate(lyrics.lines[:-1]):
            next_line = lyrics.lines[index + 1]
            gap = next_line.timestamp - line.timestamp

            if (
                gap >= gap_threshold
                and line.timestamp + start_delay <= position
                and position < next_line.timestamp
            ):
                return True

        return False
