
import json
import threading

from websockets.exceptions import ConnectionClosed
from websockets.sync.server import serve


class WebSocketServer:

    def __init__(
        self,
        on_message,
        host: str = "127.0.0.1",
        port: int = 8765,
        on_error=None
    ):
        self.host = host
        self.port = port
        self.on_message = on_message
        self.on_error = on_error

        self._server = None
        self._thread = None
        self._ready = threading.Event()
        self._startup_error = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        self._ready.clear()
        self._startup_error = None

        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self._thread.start()
        self._ready.wait()

        if self._startup_error:
            raise RuntimeError(
                "No se pudo iniciar el servidor WebSocket."
            ) from self._startup_error

    def _run(self):
        try:
            self._server = serve(
                self._handle_connection,
                self.host,
                self.port
            )

            self._ready.set()
            self._server.serve_forever()

        except Exception as error:
            self._startup_error = error
            self._ready.set()

            if self.on_error:
                self.on_error(error)

    def _handle_connection(self, websocket):
        try:
            while True:
                message = websocket.recv()

                if message is None:
                    break

                self._process_message(message)

        except ConnectionClosed:
            pass

        except Exception as error:
            if self.on_error:
                self.on_error(error)

    def _process_message(self, message):
        try:
            data = json.loads(message)

            if not isinstance(data, dict):
                raise ValueError(
                    "El mensaje debe ser un objeto JSON."
                )

            self.on_message(data)

        except (json.JSONDecodeError, ValueError) as error:
            if self.on_error:
                self.on_error(error)

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server = None

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)

        self._thread = None
