
from pathlib import Path

from models.lyrics import Lyrics
from models.song import Song
from utils.lrc_parser import parse_lrc


class LocalLyricsService:

    def load_lrc_file(
        self,
        file_path: str | Path,
        song: Song | None = None
    ) -> Lyrics:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo: {path}"
            )

        if not path.is_file():
            raise ValueError("La ruta indicada no corresponde a un archivo.")

        if path.suffix.lower() != ".lrc":
            raise ValueError("El archivo debe tener extensión .lrc.")

        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError(
                "No se pudo leer el archivo. Comprueba que esté codificado en UTF-8."
            ) from error

        lyrics = parse_lrc(content, song)

        return Lyrics(
            song=lyrics.song,
            lines=lyrics.lines,
            synced=lyrics.synced,
            source="local"
        )
