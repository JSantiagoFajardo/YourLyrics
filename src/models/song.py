from dataclasses import dataclass

@dataclass
class Song:
    title: str
    artist: str
    album: str| None = None
    year: int | None = None
    duration: int | None = None  # Duration in seconds
    source_id: str | None = None  # Source of the song (e.g., Spotify, local file)

def __post_init__(self):
        if not self.title.strip():
            raise ValueError("El título de la canción no puede estar vacío.")

        if not self.artist.strip():
            raise ValueError("El artista no puede estar vacío.")

        if self.duration is not None and self.duration <= 0:
            raise ValueError("La duración debe ser mayor que cero.")
