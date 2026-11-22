
const SERVER_URL = "ws://127.0.0.1:8765";

let socket = null;
let reconnectTimer = null;
let pendingMessage = null;

function connectWebSocket() {
    if (
        socket &&
        (socket.readyState === WebSocket.OPEN ||
         socket.readyState === WebSocket.CONNECTING)
    ) {
        return;
    }

    socket = new WebSocket(SERVER_URL);

    socket.addEventListener("open", () => {
        console.log("[YourLyrics] Conectado al servidor Python.");

        if (pendingMessage) {
            socket.send(pendingMessage);
            pendingMessage = null;
        }
    });

    socket.addEventListener("message", (event) => {
        console.log("[YourLyrics] Mensaje del servidor:", event.data);
    });

    socket.addEventListener("close", () => {
        console.log("[YourLyrics] Conexión cerrada.");
        scheduleReconnect();
    });

    socket.addEventListener("error", () => {
        console.error("[YourLyrics] Error de conexión WebSocket.");
        socket.close();
    });
}

function scheduleReconnect() {
    if (reconnectTimer !== null) {
        return;
    }

    reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        connectWebSocket();
    }, 3000);
}

chrome.runtime.onMessage.addListener((message, sender) => {
    if (message.type !== "PLAYBACK_DATA") {
        return;
    }

    if (!message.payload) {
        return;
    }

    const serialized = JSON.stringify(message.payload);

    if (socket?.readyState === WebSocket.OPEN) {
        socket.send(serialized);
    } else {
        pendingMessage = serialized;
        connectWebSocket();
    }
});

// Iniciar conexión al cargar el service worker.
connectWebSocket();
