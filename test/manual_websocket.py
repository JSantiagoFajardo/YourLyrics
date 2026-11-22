import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from controllers.playback_controller import PlaybackController
from controllers.playback_message_handler import PlaybackMessageHandler
from infrastructure.api.websocket_server import WebSocketServer


playback_controller = PlaybackController()

message_handler = PlaybackMessageHandler(
    playback_controller
)


def handle_message(data):
    playback = message_handler.handle_message(data)

    if playback.song:
        print(
            f"\nCanción: {playback.song.title}"
            f"\nArtista: {playback.song.artist}"
            f"\nPosición: {playback.position:.2f}s"
            f"\nReproduciendo: {playback.is_playing}"
            f"\nPausada: {playback.is_paused}"
        )
    else:
        print("\nNo hay ninguna canción activa.")


def handle_error(error):
    print(f"\n[ERROR] {error}")


server = WebSocketServer(
    on_message=handle_message,
    on_error=handle_error
)

try:
    server.start()

    print("YourLyrics está escuchando en 127.0.0.1:8765")
    print("Abre YouTube Music para probar la conexión.")
    print("Presiona Ctrl+C para detener el servidor.")

    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nDeteniendo YourLyrics...")

finally:
    server.stop()
