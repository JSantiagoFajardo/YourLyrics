
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve
)
from PySide6.QtGui import QFont, QColor,QFontMetrics


class LyricsWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.text_color = "#FFFFFF"
        self.text_opacity = 100
        self.font_family = "Segoe UI"

        self.shadow_enabled = True
        self.shadow_blur = 8

        # Etiquetas de sombra
        self.current_shadow = QLabel()
        self.next_shadow = QLabel()

        # Etiquetas principales
        self.current_label = QLabel("Esperando reproducción...")
        self.next_label = QLabel("...")

        #Permite que las letras ocupen varias líneas y se ajusten al ancho del widget
        self.current_label.setWordWrap(True)
        self.next_label.setWordWrap(True)
        self.current_shadow.setWordWrap(True)
        self.next_shadow.setWordWrap(True)

        for label in (
            self.current_shadow,
            self.next_shadow,
            self.current_label,
            self.next_label
        ):
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setAttribute(
                Qt.WidgetAttribute.WA_TranslucentBackground
            )

        # Efectos de sombra
        self.current_shadow_effect = QGraphicsDropShadowEffect()
        self.current_shadow_effect.setColor(QColor(0, 0, 0, 220))
        self.current_shadow_effect.setBlurRadius(self.shadow_blur)
        self.current_shadow_effect.setOffset(1, 1)

        self.next_shadow_effect = QGraphicsDropShadowEffect()
        self.next_shadow_effect.setColor(QColor(0, 0, 0, 220))
        self.next_shadow_effect.setBlurRadius(self.shadow_blur)
        self.next_shadow_effect.setOffset(1, 1)

        self.current_shadow.setGraphicsEffect(
            self.current_shadow_effect
        )
        self.next_shadow.setGraphicsEffect(
            self.next_shadow_effect
        )

        # Opacidad de las letras principales
        self.current_effect = QGraphicsOpacityEffect(
            self.current_label
        )
        self.next_effect = QGraphicsOpacityEffect(
            self.next_label
        )

        self.current_label.setGraphicsEffect(self.current_effect)
        self.next_label.setGraphicsEffect(self.next_effect)

        # Animación
        self.animation = QPropertyAnimation(
            self.current_effect, b"opacity", self
        )
        self.animation.setDuration(150)
        self.animation.setStartValue(0.25)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        # Etiquetas superpuestas
        layout = QGridLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(12)

        layout.addWidget(self.current_shadow, 0, 0)
        layout.addWidget(self.current_label, 0, 0)

        layout.addWidget(self.next_shadow, 1, 0)
        layout.addWidget(self.next_label, 1, 0)

        self.set_text_color("#FFFFFF")
        self.set_text_opacity(100)
        self.set_font_family("Segoe UI")
        self.set_shadow(True, 8)

    def set_text_color(self, color):
        self.text_color = color
        self._apply_text_style()

    def set_text_opacity(self, opacity):
        self.text_opacity = max(10, min(100, int(opacity)))

        value = self.text_opacity / 100

        self.current_effect.setOpacity(value)
        self.next_effect.setOpacity(value)

    def set_font_family(self, family):
        self.font_family = family or "Segoe UI"
        self._apply_text_style()

    def set_shadow(self, enabled, blur=8):
        self.shadow_enabled = bool(enabled)
        self.shadow_blur = max(0, min(30, int(blur)))

        self.current_shadow_effect.setBlurRadius(
            self.shadow_blur
        )
        self.next_shadow_effect.setBlurRadius(
            self.shadow_blur
        )

        self.current_shadow.setVisible(self.shadow_enabled)
        self.next_shadow.setVisible(self.shadow_enabled)

    def _apply_text_style(self):
        current_font = QFont(self.font_family, 25)
        current_font.setBold(True)

        next_font = QFont(self.font_family, 17)

        self.current_label.setFont(current_font)
        self.next_label.setFont(next_font)

        self.current_shadow.setFont(current_font)
        self.next_shadow.setFont(next_font)

        self.current_label.setStyleSheet(f"""
            color: {self.text_color};
            background: transparent;
        """)

        self.next_label.setStyleSheet(f"""
            color: {self.text_color};
            background: transparent;
        """)

        # Las etiquetas oscuras quedan detrás del texto.
        self.current_shadow.setStyleSheet("""
            color: rgba(0, 0, 0, 220);
            background: transparent;
        """)

        self.next_shadow.setStyleSheet("""
            color: rgba(0, 0, 0, 220);
            background: transparent;
        """)

    def update_lyrics(
        self,
        current_line,
        next_line=None,
        instrumental_break=False
    ):
        if instrumental_break:
            # Fuente estándar para evitar problemas con glifos.
            text = self._get_instrumental_symbol()
            next_text = ""

            current_font = QFont("Segoe UI", 21)
            current_font.setBold(True)

        elif current_line is None:
            text = "Esperando letra..."
            next_text = ""

            current_font = QFont(self.font_family, 25)
            current_font.setBold(True)

        else:
            text = current_line.text
            next_text = next_line.text if next_line else ""

            current_font = QFont(self.font_family, 25)
            current_font.setBold(True)

        if self.current_label.text() != text:
            self.animation.stop()

            self.current_effect.setOpacity(
                0.25 * (self.text_opacity / 100)
            )

            self.animation.setEndValue(
                self.text_opacity / 100
            )
            self.animation.start()

        self.current_label.setText(text)
        self.current_shadow.setText(text)

        self.next_label.setText(next_text)
        self.next_shadow.setText(next_text)

        self.current_label.setFont(current_font)
        self.current_shadow.setFont(current_font)

        self._apply_text_style()

        # Mantener la fuente estándar para el indicador.
        if instrumental_break:
            self.current_label.setFont(current_font)
            self.current_shadow.setFont(current_font)
    
    def _get_instrumental_symbol(self):
        symbols = "♫ ♪ ♫"

        font = QFont(self.font_family)

        if QFontMetrics(font).inFontUcs4(ord("♫")):
            return symbols

        return "..."   