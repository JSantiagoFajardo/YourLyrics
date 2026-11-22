from dataclasses import dataclass
from models.song import Song

@dataclass(frozen=True, slots=True)
class Playback:
    song: Song| None = None
    position: float = 0.0
    is_playing: bool = False
    is_paused: bool = False

    def __post_init__(self):
        if self.position < 0:
            raise ValueError("La posición de reproducción no puede ser negativa.")
        if self.is_paused and self.is_playing:
            raise ValueError("La reproducción no puede estar en pausa y en reproducción al mismo tiempo.")
        