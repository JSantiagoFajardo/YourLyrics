
from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    playback_updated = Signal()
