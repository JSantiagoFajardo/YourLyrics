
from models.playback import Playback
from models.song import Song


class PlaybackController:

    def __init__(self):
        self._playback = Playback()

    @property
    def current_playback(self) -> Playback:
        return self._playback

    def update_playback(
        self,
        song: Song | None,
        position: float,
        is_playing: bool,
        is_paused: bool
    ) -> Playback:

        self._playback = Playback(
            song=song,
            position=position,
            is_playing=is_playing,
            is_paused=is_paused
        )

        return self._playback

    def update_position(self, position: float) -> Playback:
        self._playback = Playback(
            song=self._playback.song,
            position=position,
            is_playing=self._playback.is_playing,
            is_paused=self._playback.is_paused
        )

        return self._playback

    def set_playing(self) -> Playback:
        self._playback = Playback(
            song=self._playback.song,
            position=self._playback.position,
            is_playing=True,
            is_paused=False
        )

        return self._playback

    def set_paused(self) -> Playback:
        self._playback = Playback(
            song=self._playback.song,
            position=self._playback.position,
            is_playing=False,
            is_paused=True
        )

        return self._playback

    def stop(self) -> Playback:
        self._playback = Playback()

        return self._playback
