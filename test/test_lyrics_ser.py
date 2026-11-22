import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from models.song import Song
from services.lyrics_service import LyricsService


def main():
    song = Song(
        title="Shanghai Night",
        artist="Joost",
        duration=None
    )
    print("\n--- DIAGNÓSTICO ---")
    print("Clase del objeto:", type(song))
    print("Módulo del objeto:", type(song).__module__)
    print("¿Es Song?:", isinstance(song, Song))

    import services.lyrics_service as ls

    print("Clase Song del servicio:", ls.Song)
    print("¿Coinciden las clases?:", Song is ls.Song)
    service = LyricsService(
        client=type(
            "FakeLRCLIB",
            (),
            {
                "search_lyrics": lambda self, **kwargs: None,
                "search_synced_lyrics": lambda self, **kwargs: None,
            }
        )()
    )

    print("\nBuscando letras...")
    print(f"Canción: {song.title}")
    print(f"Artista: {song.artist}")

    try:
        lyrics = service.get_lyrics(song)

        print("\n¡Letras encontradas!")
        print(f"Proveedor: {lyrics.source}")
        print(f"Sincronizadas: {lyrics.synced}")
        print(f"Cantidad de líneas: {len(lyrics.lines)}")

        print("\nPrimeras líneas:")
        for line in lyrics.lines[:10]:
            print(f"[{line.timestamp:.2f}] {line.text}")

    except Exception as error:
        print("\nNo se pudieron obtener las letras.")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
