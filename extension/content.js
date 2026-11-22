
(() => {
    const PLAYER_SELECTOR = "video";
    const UPDATE_INTERVAL = 1000;

    let lastMessage = "";
    let lastTrackId = null;

    function getSongMetadata() {
        const playerBar = document.querySelector("ytmusic-player-bar");

        const titleElement = playerBar?.querySelector(".title");

        const artistElement = playerBar?.querySelector(
            ".subtitle yt-formatted-string.byline"
        );

        const title = titleElement?.textContent?.trim();

        const artist = artistElement?.textContent
            ?.split("•")[0]
            .trim();

        if (!title || !artist) {
            return null;
        }

        return { title, artist };
    }

    function getPlaybackData() {
        const video = document.querySelector(PLAYER_SELECTOR);
        
        if (!video) {
            return null;
        }

        const song = getSongMetadata();

        if (!song) {
            return null;
        }
        console.log("[DEBUG PLAYER]", {
            currentTime: video.currentTime,
            paused: video.paused,
            duration: video.duration
        });
        return {
            type: "playback_update",
            title: song.title,
            artist: song.artist,
            track_id: `${song.artist}::${song.title}`,
            duration: Number.isFinite(video.duration)
                ? video.duration
                : null,
            position: video.currentTime || 0,
            is_playing: !video.paused && !video.ended,
            is_paused: video.paused,
            source_id: window.location.href
        };
    }

    function sendPlaybackData() {
        const data = getPlaybackData();

        if (!data) {
            return;
        }

        const trackChanged = data.track_id !== lastTrackId;

        if (trackChanged) {
            lastTrackId = data.track_id;
            lastMessage = "";

            console.log(
                "[YourLyrics] Nueva canción detectada:",
                data.track_id,
                "Posición:",
                data.position
            );
        }

        const serialized = JSON.stringify(data);

        if (serialized === lastMessage) {
            return;
        }

        lastMessage = serialized;

        chrome.runtime.sendMessage({
            type: "PLAYBACK_DATA",
            payload: data
        }).catch(() => {});
    }

    // Envío periódico de datos de reproducción.
    setInterval(sendPlaybackData, UPDATE_INTERVAL);

    // Detectar cambios en los metadatos del reproductor.
    const observer = new MutationObserver(() => {
        sendPlaybackData();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });

    // Primer envío.
    sendPlaybackData();

})();
