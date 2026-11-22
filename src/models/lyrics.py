from dataclasses import dataclass
from models.lyric_line import LyricLine
from models.song import Song

@dataclass(frozen=True, slots=True)
class Lyrics:
    song: Song
    lines: tuple[LyricLine, ...]
    synced: bool = True
    source: str | None = None

    def __post_init__(self):
        if not self.lines:
            raise ValueError("La lista de líneas de letra no puede estar vacía.")
        
    
        if not all(isinstance(line, LyricLine) for line in self.lines):
            raise TypeError("Todos los elementos de la lista de líneas deben ser instancias de LyricLine.")
    
        timestamps = [line.timestamp for line in self.lines]
        
        if timestamps != sorted(timestamps):
            raise ValueError("Las líneas deben estar ordenadas por timestamp.")
        