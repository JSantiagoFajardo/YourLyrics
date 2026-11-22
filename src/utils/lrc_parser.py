
import re

from models.lyric_line import LyricLine
from models.lyrics import Lyrics
from models.song import Song
from utils.time_parser import timestamp_to_seconds


TIMESTAMP_PATTERN = re.compile(
    r"\[(\d{2,}:[0-5]\d(?:[.:]\d{1,3})?)\]"
)

METADATA_PATTERN = re.compile(
    r"^\[([a-zA-Z]{2}):([^\]]*)\]\s*$"
)


def parse_lrc(content: str, song: Song | None = None) -> Lyrics:
    """
    Convierte el contenido de un archivo LRC en un objeto Lyrics.

    Si no se proporciona una canción, utiliza los metadatos
    [ti], [ar] y [al] para construirla.
    """

    if not isinstance(content, str):
        raise TypeError("El contenido LRC debe ser una cadena de texto.")

    if not content.strip():
        raise ValueError("El contenido LRC está vacío.")

    metadata = {}
    lines = []

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        metadata_match = METADATA_PATTERN.match(line)

        if metadata_match:
            tag = metadata_match.group(1).lower()
            value = metadata_match.group(2).strip()

            if tag in ("ti", "ar", "al"):
                metadata[tag] = value

            continue

        timestamps = []
        position = 0

        while match := TIMESTAMP_PATTERN.match(line, position):
            timestamp = f"[{match.group(1)}]"
            timestamps.append(timestamp_to_seconds(timestamp))
            position = match.end()

        if not timestamps:
            continue

        lyric_text = line[position:].strip()

        if not lyric_text:
            continue

        for timestamp in timestamps:
            lines.append(
                LyricLine(
                    timestamp=timestamp,
                    text=lyric_text
                )
            )

    if not lines:
        raise ValueError("No se encontraron líneas de letra con timestamps.")

    if song is None:
        title = metadata.get("ti")
        artist = metadata.get("ar")
        album = metadata.get("al")

        if not title or not artist:
            raise ValueError(
                "El LRC debe incluir los metadatos [ti] y [ar] "
                "si no se proporciona un objeto Song."
            )

        song = Song(
            title=title,
            artist=artist,
            album=album
        )

    elif not isinstance(song, Song):
        raise TypeError("El parámetro song debe ser una instancia de Song.")

    lines.sort(key=lambda lyric: lyric.timestamp)

    return Lyrics(
        song=song,
        lines=tuple(lines),
        synced=True,
        source="LRC"
    )
