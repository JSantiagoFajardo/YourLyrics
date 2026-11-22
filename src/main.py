
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

sys.path.insert(0, str(Path(__file__).resolve().parent))

from views.main_window import MainWindow

from controllers.playback_controller import PlaybackController
from controllers.lyrics_controller import LyricsController
from controllers.lyrics_sync_controller import LyricsSyncController
from controllers.playback_message_handler import PlaybackMessageHandler

from services.lyrics_service import LyricsService
from services.lyrics_synchronization_service import LyricsSyncService

from infrastructure.api.websocket_server import WebSocketServer


def main():

    app = QApplication(sys.argv)

    # Servicios
    lyrics_service = LyricsService()
    sync_service = LyricsSyncService()

    # Controladores
    playback_controller = PlaybackController()

    lyrics_controller = LyricsController(
        lyrics_service=lyrics_service
    )

    sync_controller = LyricsSyncController(
        lyrics_controller,
        playback_controller,
        sync_service
    )

    # Ventana
    window = MainWindow()
    window.show()

    # Procesamiento en segundo plano
    executor = ThreadPoolExecutor(max_workers=2)
    lyrics_queue = Queue()

    last_requested_song = None

    # Handler de reproducción
    message_handler = PlaybackMessageHandler(
        playback_controller
    )

    def fetch_lyrics(song):

        try:
            lyrics = lyrics_service.get_lyrics(song)
            lyrics_queue.put((song, lyrics, None))

        except Exception as error:
            lyrics_queue.put((song, None, str(error)))

    def on_message(data):

        nonlocal last_requested_song

        message_handler.handle_message(data)
        playback = playback_controller.current_playback

        if playback.song:
            print(
                f"[YourLyrics] Reproduciendo: "
                f"{playback.song.title} - {playback.song.artist}"
            )
        playback = playback_controller.current_playback
        song = playback.song

        if song is None:
            return

        song_key = (song.title, song.artist)

        if song_key == last_requested_song:
            return

        last_requested_song = song_key
        lyrics_controller.clear_lyrics()
        print(
            f"[YourLyrics] Buscando letras, Nueva canción detectada: "
            f"{song.title} - {song.artist}"
        )

        executor.submit(fetch_lyrics, song)

    # Servidor WebSocket
    server = WebSocketServer(
        on_message=on_message
    )

    server.start()

    # Actualización de interfaz
    def update_interface():

        current_playback = playback_controller.current_playback
        current_song = current_playback.song
        window.update_metadata(current_song)
        
        # Procesar resultados de LRCLIB
        while not lyrics_queue.empty():

            song, lyrics, error = lyrics_queue.get()

            # Ignorar resultados de canciones anteriores
            if current_song is None:
                continue

            if (
                song.title != current_song.title
                or song.artist != current_song.artist
            ):
                continue

            if error:
                print(f"[YourLyrics] Error buscando letras: {error}")
                continue

            lyrics_controller.set_lyrics(lyrics)

            print("[YourLyrics] Letras cargadas correctamente.")

        # Actualizar letras
        current_line, next_line = (sync_controller.get_current_and_next_lines())

        instrumental_break = (sync_controller.is_instrumental_break())
        if current_line:
            print(
                f"[SYNC] Posición: {current_playback.position:.2f} | "
                f"Línea: {current_line.timestamp:.2f} | "
                f"Texto: {current_line.text}"
            )
        else:
            print(
                f"[SYNC] Sin línea actual | "
                f"Posición: {current_playback.position:.2f}"
            )
        window.lyrics_widget.update_lyrics(current_line,next_line,instrumental_break)
        window.adjust_window_height()
    timer = QTimer()
    timer.timeout.connect(update_interface)
    timer.start(200)

    # Cierre
    app.aboutToQuit.connect(server.stop)
    app.aboutToQuit.connect(
        lambda: executor.shutdown(wait=False)
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
