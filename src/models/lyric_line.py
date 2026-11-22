from dataclasses import dataclass
@dataclass(frozen=True, slots=True)
class LyricLine:
    timestamp: float
    text: str 

    def __post_init__(self):
        if not self.text.strip():
            raise ValueError("El texto de la línea de letra no puede estar vacío.")

        if self.timestamp < 0:
            raise ValueError("La marca de tiempo no puede ser negativa.")
    