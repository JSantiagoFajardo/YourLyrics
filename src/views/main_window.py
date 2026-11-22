
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    
)
from pathlib import Path
from PySide6.QtCore import Qt, QPoint, QSettings
from PySide6.QtGui import QColor,QPainter,QFontDatabase

from views.lyrics_widget import LyricsWidget
from views.settings_dialog import SettingsDialog


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.lyrics_widget = LyricsWidget()
        self._drag_position = QPoint()
        self.settings = QSettings("YourLyrics", "YourLyrics")
        self.shadow_enabled = self._setting_bool("shadow_enabled", True)

        self.shadow_blur = int(self.settings.value("shadow_blur", 8))
        self.font_family = self.settings.value("font_family", "Segoe UI")

        self.window_opacity = int(
            self.settings.value("window_opacity", 85)
        )
        self.text_opacity = int(
            self.settings.value("text_opacity", 100)
        )
        self.text_opacity_enabled = self._setting_bool(
            "text_opacity_enabled", False
        )
        self.text_color = self.settings.value(
            "text_color", "#FFFFFF"
        )
        self.background_color = self.settings.value(
            "background_color", "#181A20"
        )
        self.show_metadata = self._setting_bool(
            "show_metadata", True
        )
        self.lyrics_only = self._setting_bool(
            "lyrics_only", False
        )

        self._setup_window()
        self._setup_layout()
        self._apply_settings()

    def _setting_bool(self, key, default):
        value = self.settings.value(key, default)
        self._load_custom_fonts()

        if isinstance(value, bool):
            return value

        return str(value).lower() in ("true", "1", "yes")

    def _setup_window(self):
        self.setObjectName("mainWindow")
        self.setWindowTitle("YourLyrics")

        # Permite transparencia real en Windows.
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground,True)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.resize(650, 230)

        # Clic derecho sobre la ventana abre configuración.
        self.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.customContextMenuRequested.connect(
            lambda _: self._open_settings()
        )

    def _connect_settings_context_menu(self, widget):
        widget.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        widget.customContextMenuRequested.connect(
            lambda _: self._open_settings()
        )

    def _setup_layout(self):

        # Letras
        self._connect_settings_context_menu(self.lyrics_widget)
        self._connect_settings_context_menu(self.lyrics_widget.current_label)
        self._connect_settings_context_menu(self.lyrics_widget.next_label)

        self.header = QHBoxLayout()

        self.title_label = QLabel("YourLyrics")
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)

        # Botones
        self.settings_button = QPushButton("⚙")
        self.settings_button.setToolTip("Configuración")
        self.settings_button.clicked.connect(self._open_settings)

        self.compact_button = QPushButton("◉")
        self.compact_button.setToolTip("Modo solo letras")
        self.compact_button.clicked.connect(
            self._toggle_lyrics_only
        )

        self.minimize_button = QPushButton("—")
        self.minimize_button.clicked.connect(self.showMinimized)

        self.maximize_button = QPushButton("□")
        self.maximize_button.clicked.connect(self._toggle_maximize)

        self.close_button = QPushButton("×")
        self.close_button.clicked.connect(self.close)

        self.header.addWidget(self.title_label)
        self.header.addStretch()
        self.header.addWidget(self.compact_button)
        self.header.addWidget(self.settings_button)
        self.header.addWidget(self.minimize_button)
        self.header.addWidget(self.maximize_button)
        self.header.addWidget(self.close_button)

        # Metadatos
        self.song_title_label = QLabel("")
        self.song_details_label = QLabel(
            "Esperando reproducción..."
        )

        self.song_title_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )
        self.song_details_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        self.metadata_container = QWidget()

        metadata_layout = QVBoxLayout(self.metadata_container)
        metadata_layout.setContentsMargins(0, 0, 0, 0)
        metadata_layout.setSpacing(3)

        metadata_layout.addWidget(self.song_title_label)
        metadata_layout.addWidget(self.song_details_label)

        self.song_title_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)

        self.song_details_label.setStyleSheet("""
            color: #A0A0A0;
            font-size: 11px;
            background: transparent;
        """)

        self._connect_settings_context_menu(
            self.song_title_label
        )
        self._connect_settings_context_menu(
            self.song_details_label
        )

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(self.metadata_container)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 10, 15, 12)
        self.main_layout.setSpacing(5)

        self.main_layout.addLayout(self.header)
        self.main_layout.addWidget(self.lyrics_widget, 1)
        self.main_layout.addLayout(footer)

    
    def _apply_settings(self):

        self._background_color = QColor(self.background_color)

        if self.lyrics_only:
            self._background_color.setAlpha(0)
        else:
            alpha = round(255 * self.window_opacity / 100)
            self._background_color.setAlpha(alpha)

        # Estilos de los controles, sin pintar el fondo de la ventana.
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                font-size: 16px;
                border: none;
                padding: 5px;
            }

            QPushButton:hover {
                background-color: rgba(80, 80, 80, 150);
                border-radius: 5px;
            }
        """)

        self.lyrics_widget.set_text_color(self.text_color)
        self.lyrics_widget.set_font_family(self.font_family)
        self.lyrics_widget.set_shadow(self.shadow_enabled,self.shadow_blur)
        effective_opacity = (
            self.text_opacity
            if self.text_opacity_enabled
            else 100
        )

        self.lyrics_widget.set_text_opacity(effective_opacity)

        self.metadata_container.setVisible(self.show_metadata)

        self._apply_display_mode()
        self.update()
    
    def _apply_display_mode(self):

        # Ocultar controles en modo solo letras.
        self.title_label.setVisible(not self.lyrics_only)
        self.compact_button.setVisible(not self.lyrics_only)

        self.minimize_button.setVisible(not self.lyrics_only)
        self.maximize_button.setVisible(not self.lyrics_only)
        self.close_button.setVisible(not self.lyrics_only)

        # La ruedita también se oculta.
        # La configuración se abre con clic derecho sobre las letras.
        self.settings_button.setVisible(not self.lyrics_only)

        if self.lyrics_only:

            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)

            if self.show_metadata:
                self.resize(600, 150)
            else:
                self.resize(600, 100)

        else:

            self.main_layout.setContentsMargins(
                15, 10, 15, 12
            )
            self.main_layout.setSpacing(5)

            self.resize(650, 230)

        self.update()

    def _toggle_lyrics_only(self):

        self.lyrics_only = not self.lyrics_only

        self.settings.setValue(
            "lyrics_only", self.lyrics_only
        )

        self._apply_settings()

    def _open_settings(self):

        dialog = SettingsDialog(
            window_opacity=self.window_opacity,
            text_opacity=self.text_opacity,
            text_opacity_enabled=self.text_opacity_enabled,
            text_color=self.text_color,
            background_color=self.background_color,
            show_metadata=self.show_metadata,
            lyrics_only=self.lyrics_only,
            parent=self,
            shadow_enabled=self.shadow_enabled,
            shadow_blur=self.shadow_blur,
            font_family=self.font_family
        )
        
        if dialog.exec():

            values = dialog.get_settings()
            self.shadow_enabled = values["shadow_enabled"]
            self.shadow_blur = values["shadow_blur"]
            self.font_family = values["font_family"]
            self.window_opacity = values["window_opacity"]
            self.text_opacity = values["text_opacity"]
            self.text_opacity_enabled = (
                values["text_opacity_enabled"]
            )
            self.text_color = values["text_color"]
            self.background_color = values["background_color"]
            self.show_metadata = values["show_metadata"]
            self.lyrics_only = values["lyrics_only"]

            for key, value in values.items():
                self.settings.setValue(key, value)

            self._apply_settings()

    def update_metadata(self, song):

        if song is None:
            self.song_title_label.setText("")
            self.song_details_label.setText(
                "Esperando reproducción..."
            )
            return

        self.song_title_label.setText(song.title)

        details = song.artist

        if song.album:
            details += f"  •  {song.album}"

        self.song_details_label.setText(details)

    def _toggle_maximize(self):

        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._background_color)

        painter.drawRoundedRect(
            self.rect(),
            10,
            10
        )

        painter.end()

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):

        if event.buttons() & Qt.MouseButton.LeftButton:

            if not self.isMaximized():
                self.move(
                    event.globalPosition().toPoint()
                    - self._drag_position
                )
                event.accept()

    def _load_custom_fonts(self):

        fonts_dir = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "fonts"
        )

        if not fonts_dir.exists():
            return

        for font_file in fonts_dir.iterdir():

            if font_file.suffix.lower() not in (".ttf", ".otf"):
                continue

            QFontDatabase.addApplicationFont(str(font_file))
   
    def adjust_window_height(self):
        if self.lyrics_only:
            self.lyrics_widget.adjustSize()

            required_height = self.lyrics_widget.sizeHint().height() + 40

            self.resize(
                self.width(),
                max(120, required_height)
            )