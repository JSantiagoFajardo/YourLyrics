
from controllers.lyrics_controller import LyricsController
from controllers.playback_controller import PlaybackController
from services.lyrics_synchronization_service import LyricsSyncService


class LyricsSyncController:

    def __init__(
        self,
        lyrics_controller: LyricsController,
        playback_controller: PlaybackController,
        sync_service: LyricsSyncService | None = None
    ):
        self._lyrics_controller = lyrics_controller
        self._playback_controller = playback_controller
        self._sync_service = sync_service or LyricsSyncService()

    def _same_song(self, lyrics, playback):
        if lyrics is None or playback.song is None:
            return False

        lyrics_song = lyrics.song
        playback_song = playback.song

        return (
            lyrics_song.title.strip().casefold()
            == playback_song.title.strip().casefold()
            and
            lyrics_song.artist.strip().casefold()
            == playback_song.artist.strip().casefold()
        )

    def get_current_line(self):
        lyrics = self._lyrics_controller.current_lyrics
        playback = self._playback_controller.current_playback

        if not self._same_song(lyrics, playback):
            return None

        return self._sync_service.get_current_line(
            lyrics,
            playback.position
        )

    def get_current_and_next_lines(self):
        lyrics = self._lyrics_controller.current_lyrics
        playback = self._playback_controller.current_playback

        if not self._same_song(lyrics, playback):
            return None, None

        current_line = self._sync_service.get_current_line(
            lyrics,
            playback.position
        )

        next_line = self._sync_service.get_next_line(
            lyrics,
            playback.position
        )

        return current_line, next_line

    def is_instrumental_break(self):
        lyrics = self._lyrics_controller.current_lyrics
        playback = self._playback_controller.current_playback

        if not self._same_song(lyrics, playback):
            return False

        return self._sync_service.is_instrumental_break(
            lyrics,
            playback.position
        )