import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.infrastructure.api.netease_client import NetEaseClient

client = NetEaseClient()

result = client.search_lyrics(
    title="夜のピエロ",
    artist="Ado"
)

if result:
    print("NetEase respondió correctamente.")
    print("ID:", result["song_id"])
    print("Origen:", result["source"])
    print("Primeras líneas:")
    print("\n".join(result["syncedLyrics"].splitlines()[:5]))
else:
    print("No se encontraron letras sincronizadas.")
