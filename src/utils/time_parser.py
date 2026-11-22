
import re


TIMESTAMP_PATTERN = re.compile(
    r"^\[(\d{2,}):([0-5]\d)(?:[.:](\d{1,3}))?\]$"
)


def timestamp_to_seconds(timestamp: str) -> float:
    """
    Convierte un timestamp LRC a segundos.
    """

    match = TIMESTAMP_PATTERN.match(timestamp.strip())

    if not match:
        raise ValueError(f"Timestamp LRC inválido: {timestamp}")

    minutes = int(match.group(1))
    seconds = int(match.group(2))
    fraction = match.group(3) or "0"

    # Normaliza fracciones a milisegundos.
    milliseconds = int(fraction.ljust(3, "0"))

    return minutes * 60 + seconds + milliseconds / 1000
