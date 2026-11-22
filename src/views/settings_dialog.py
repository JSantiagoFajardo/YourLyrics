
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QSlider,
    QPushButton, QColorDialog, QDialogButtonBox, QCheckBox,
    QFrame, QHBoxLayout, QComboBox, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase


class SettingsDialog(QDialog):

    def __init__(
        self,
        window_opacity=85,
        text_opacity=100,
        text_opacity_enabled=False,
        text_color="#FFFFFF",
        background_color="#181A20",
        show_metadata=True,
        lyrics_only=False,
        font_family="Segoe UI",
        parent=None,
        shadow_enabled=True,
        shadow_blur=8
    ):
        super().__init__(parent)

        self.setWindowTitle("YourLyrics | Configuración")
        self.setFixedWidth(420)

        self.text_color = QColor(text_color)
        self.background_color = QColor(background_color)

        self.available_fonts = self._load_fonts()

        self.setStyleSheet("""
            QDialog {
                background-color: #181A20;
                color: #F1F1F1;
                font-family: Segoe UI;
                font-size: 10pt;
            }

            QLabel {
                color: #D8D9DE;
            }

            QCheckBox {
                color: #D8D9DE;
                spacing: 8px;
            }

            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }

            QPushButton {
                background-color: #292C35;
                color: #F1F1F1;
                border: 1px solid #3B3F4A;
                border-radius: 7px;
                padding: 7px 12px;
            }

            QPushButton:hover {
                background-color: #383C48;
                border-color: #626879;
            }

            QComboBox {
                background-color: #292C35;
                color: #F1F1F1;
                border: 1px solid #3B3F4A;
                border-radius: 7px;
                padding: 7px;
            }

            QComboBox QAbstractItemView {
                background-color: #292C35;
                color: #F1F1F1;
                selection-background-color: #526BAA;
            }

            QSlider::groove:horizontal {
                height: 5px;
                background: #3B3F4A;
                border-radius: 2px;
            }

            QSlider::sub-page:horizontal {
                background: #8297D8;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                background: #FFFFFF;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }

            QFrame#preview {
                background-color: #252832;
                border: 1px solid #3B3F4A;
                border-radius: 10px;
            }

            QDialogButtonBox QPushButton {
                min-width: 85px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(15)

        title = QLabel("Personaliza tu experiencia")
        title.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #FFFFFF;"
        )

        subtitle = QLabel(
            "Ajusta la apariencia de las letras y de la ventana."
        )
        subtitle.setStyleSheet("color: #9298A6; font-size: 9pt;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setVerticalSpacing(13)
        form.setHorizontalSpacing(12)

        # Opacidad de la ventana
        self.window_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.window_opacity_slider.setRange(10, 100)
        self.window_opacity_slider.setValue(window_opacity)

        self.window_opacity_label = QLabel(f"{window_opacity}%")

        window_layout = QVBoxLayout()
        window_layout.addWidget(self.window_opacity_slider)
        window_layout.addWidget(self.window_opacity_label)

        form.addRow("Opacidad de la ventana:", window_layout)

        # Opacidad de las letras
        self.text_opacity_enabled = QCheckBox(
            "Permitir modificar la opacidad de las letras"
        )
        self.text_opacity_enabled.setChecked(text_opacity_enabled)

        self.text_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_opacity_slider.setRange(10, 100)
        self.text_opacity_slider.setValue(text_opacity)

        self.text_opacity_label = QLabel(f"{text_opacity}%")

        text_layout = QVBoxLayout()
        text_layout.addWidget(self.text_opacity_enabled)
        text_layout.addWidget(self.text_opacity_slider)
        text_layout.addWidget(self.text_opacity_label)

        form.addRow("Opacidad de las letras:", text_layout)

        # Tipografía
        self.font_combo = QComboBox()

        for display_name, family in self.available_fonts:
            self.font_combo.addItem(display_name, family)

        index = self.font_combo.findData(font_family)

        if index < 0:
            index = self.font_combo.findData("Segoe UI")

        self.font_combo.setCurrentIndex(max(0, index))

        form.addRow("Fuente de las letras:", self.font_combo)

        # Colores
        self.text_color_button = QPushButton("Elegir color")
        self.text_color_button.clicked.connect(self._select_text_color)
        form.addRow("Color de las letras:", self.text_color_button)

        self.background_color_button = QPushButton("Elegir color")
        self.background_color_button.clicked.connect(
            self._select_background_color
        )
        form.addRow("Color de fondo:", self.background_color_button)

        # Opciones de visualización
        self.show_metadata_checkbox = QCheckBox(
            "Mostrar artista, canción y álbum"
        )
        self.show_metadata_checkbox.setChecked(show_metadata)
        form.addRow(self.show_metadata_checkbox)

        self.lyrics_only_checkbox = QCheckBox(
            "Activar modo solo letras"
        )
        self.lyrics_only_checkbox.setChecked(lyrics_only)
        form.addRow(self.lyrics_only_checkbox)

        layout.addLayout(form)

        # Vista previa
        preview_title = QLabel("Vista previa")
        preview_title.setStyleSheet(
            "font-size: 11pt; font-weight: bold; color: #FFFFFF;"
        )
        layout.addWidget(preview_title)

        self.preview = QFrame()
        self.preview.setObjectName("preview")
        self.preview.setMinimumHeight(115)

        preview_layout = QVBoxLayout(self.preview)
        preview_layout.setContentsMargins(12, 12, 12, 10)

        self.preview_current = QLabel("Y aunque pase el tiempo...")
        self.preview_next = QLabel("la música sigue aquí")
        self.preview_metadata = QLabel("Artista  •  Canción  •  Álbum")

        self.preview_current.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_next.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_metadata.setAlignment(Qt.AlignmentFlag.AlignRight)

        preview_layout.addWidget(self.preview_current)
        preview_layout.addWidget(self.preview_next)
        preview_layout.addWidget(self.preview_metadata)

        layout.addWidget(self.preview)
        
        # Sombra de las letras
        self.shadow_checkbox = QCheckBox(
            "Activar sombra detrás de las letras"
        )
        self.shadow_checkbox.setChecked(shadow_enabled)

        self.shadow_blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.shadow_blur_slider.setRange(0, 30)
        self.shadow_blur_slider.setValue(shadow_blur)

        self.shadow_blur_label = QLabel(f"{shadow_blur}")        

        # Actualización en vivo
        self.window_opacity_slider.valueChanged.connect(self._update_preview)
        self.text_opacity_slider.valueChanged.connect(self._update_preview)
        self.text_opacity_enabled.stateChanged.connect(self._update_preview)
        self.shadow_checkbox.stateChanged.connect(self._update_preview)
        self.shadow_blur_slider.valueChanged.connect(self._update_preview)
        self.show_metadata_checkbox.stateChanged.connect(
            self._update_preview
        )
        self.font_combo.currentIndexChanged.connect(self._update_preview)
        

        shadow_layout = QVBoxLayout()
        shadow_layout.addWidget(self.shadow_checkbox)
        shadow_layout.addWidget(self.shadow_blur_slider)
        shadow_layout.addWidget(self.shadow_blur_label)

        form.addRow("Sombra del texto:", shadow_layout)
        # Botones de color
        self.window_opacity_slider.valueChanged.connect(
            lambda _: self._update_preview()
        )

        # Botones de diálogo
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self._update_color_buttons()
        self._update_preview()

    def _load_fonts(self):
        fonts_dir = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "fonts"
        )

        fonts = {
            "Segoe UI": "Segoe UI"
        }

        # Cargar automáticamente todos los TTF y OTF.
        if fonts_dir.exists():
            for font_file in sorted(fonts_dir.iterdir()):
                if font_file.suffix.lower() not in (".ttf", ".otf"):
                    continue

                font_id = QFontDatabase.addApplicationFont(
                    str(font_file)
                )

                if font_id < 0:
                    continue

                families = QFontDatabase.applicationFontFamilies(
                    font_id
                )

                for family in families:
                    fonts[family] = family

        preferred_order = [
            "Segoe UI",
            "Kiwi Soda",
            "VCR OSD Mono",
            "Saltblack Combat",
            "Blue Screen",
            "Starborn",
            "Bleeding Cowboys"
        ]

        result = []

        for preferred in preferred_order:
            for family in fonts:
                if family.lower() == preferred.lower():
                    result.append((preferred, family))
                    break

        # Incluir automáticamente futuras fuentes.
        for family in sorted(fonts):
            if not any(existing[1] == family for existing in result):
                result.append((family, family))

        return result

    def _select_text_color(self):
        color = QColorDialog.getColor(
            self.text_color,
            self,
            "Seleccionar color de las letras"
        )

        if color.isValid():
            self.text_color = color
            self._update_color_buttons()
            self._update_preview()

    def _select_background_color(self):
        color = QColorDialog.getColor(
            self.background_color,
            self,
            "Seleccionar color de fondo"
        )

        if color.isValid():
            self.background_color = color
            self._update_color_buttons()
            self._update_preview()

    def _update_color_buttons(self):
        self.text_color_button.setStyleSheet(
            f"background-color: {self.text_color.name()};"
            "color: #333333; border-radius: 7px; padding: 7px;"
        )

        self.background_color_button.setStyleSheet(
            f"background-color: {self.background_color.name()};"
            "color: #FFFFFF; border-radius: 7px; padding: 7px;"
        )

    def _update_preview(self, *_):
        window_opacity = self.window_opacity_slider.value()

        text_opacity = (
            self.text_opacity_slider.value()
            if self.text_opacity_enabled.isChecked()
            else 100
        )

        self.window_opacity_label.setText(f"{window_opacity}%")
        self.text_opacity_label.setText(f"{text_opacity}%")

        background = QColor(self.background_color)
        background.setAlpha(round(window_opacity * 2.55))

        text = QColor(self.text_color)
        text.setAlpha(round(text_opacity * 2.55))

        self.preview.setStyleSheet(
            "QFrame#preview {"
            f"background-color: {background.name(QColor.NameFormat.HexArgb)};"
            "border: 1px solid #3B3F4A; border-radius: 10px;"
            "}"
        )

        family = self.font_combo.currentData() or "Segoe UI"

        self.preview_current.setFont(QFont(family, 16, QFont.Weight.Bold))
        self.preview_next.setFont(QFont(family, 12))
        self.preview_metadata.setFont(QFont(family, 9))

        self.preview_current.setStyleSheet(
            f"color: {text.name(QColor.NameFormat.HexArgb)};"
            "background: transparent;"
        )

        self.preview_next.setStyleSheet(
            f"color: {text.name(QColor.NameFormat.HexArgb)};"
            "background: transparent;"
        )

        self.preview_metadata.setStyleSheet(
            f"color: {text.name(QColor.NameFormat.HexArgb)};"
            "background: transparent;"
        )
        #
        self.shadow_blur_label.setText(str(self.shadow_blur_slider.value()))
        shadow_effect = QGraphicsDropShadowEffect(self.preview_current)
        shadow_effect.setColor(QColor(0, 0, 0, 220))
        shadow_effect.setBlurRadius(self.shadow_blur_slider.value())
        shadow_effect.setOffset(1, 1)

        self.preview_current.setGraphicsEffect(shadow_effect)

        self.preview_current.setGraphicsEffect(
            shadow_effect if self.shadow_checkbox.isChecked() else None
        )

        self.preview_metadata.setVisible(
            self.show_metadata_checkbox.isChecked()
        )

        self.text_opacity_slider.setEnabled(
            self.text_opacity_enabled.isChecked()
        )

    def get_settings(self):
        return {
            "window_opacity": self.window_opacity_slider.value(),
            "text_opacity": self.text_opacity_slider.value(),
            "text_opacity_enabled": self.text_opacity_enabled.isChecked(),
            "text_color": self.text_color.name(),
            "background_color": self.background_color.name(),
            "show_metadata": self.show_metadata_checkbox.isChecked(),
            "lyrics_only": self.lyrics_only_checkbox.isChecked(),
            "font_family": self.font_combo.currentData(),
            "shadow_enabled": self.shadow_checkbox.isChecked(),
            "shadow_blur": self.shadow_blur_slider.value()
        }
