from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QPixmap


def _ms_to_mmss(ms: int) -> str:
    s = max(0, ms // 1000)
    return f"{s // 60}:{s % 60:02d}"


class IconButton(QPushButton):
    """Yuvarlak, borderless buton — shuffle, prev, next, repeat için."""

    def __init__(self, text: str, size: int = 36, font_size: int = 14, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._base_opacity = 0.55
        self._hover_opacity = 1.0
        self._font_size = font_size
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(f"""
            IconButton {{
                background-color: transparent;
                color: rgba(255, 255, 255, {int(self._base_opacity * 255)});
                border: none;
                border-radius: {self.width() // 2}px;
                font-size: {self._font_size}px;
                font-weight: 500;
            }}
            IconButton:hover {{
                color: rgba(255, 255, 255, {int(self._hover_opacity * 255)});
                background-color: rgba(255, 255, 255, 12);
            }}
            IconButton:pressed {{
                background-color: rgba(255, 255, 255, 20);
            }}
        """)


class PlayButton(QPushButton):
    """Büyük, yeşil/siyah play/pause butonu — Spotify/Apple Music tarzı."""

    def __init__(self, parent=None):
        super().__init__("▶", parent)
        self.setFixedSize(56, 56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            PlayButton {
                background-color: #1db954;
                color: #000000;
                border: none;
                border-radius: 28px;
                font-size: 22px;
                font-weight: 700;
            }
            PlayButton:hover {
                background-color: #1ed760;
                transform: scale(1.05);
            }
            PlayButton:pressed {
                background-color: #169c46;
                transform: scale(0.97);
            }
        """)


class Controls(QWidget):
    seek_requested = pyqtSignal(int)      # ms
    volume_changed = pyqtSignal(int)      # 0-100
    skip_backward = pyqtSignal()          # 10s geri
    skip_forward = pyqtSignal()           # 10s ileri
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._is_playing = False
        self._user_seeking = False

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 10, 32, 24)
        root.setSpacing(10)

        # ── Seek row ──
        seek_row = QHBoxLayout()
        seek_row.setSpacing(10)

        self.time_label = QLabel("0:00")
        self.time_label.setObjectName("timeLabel")
        self.duration_label = QLabel("0:00")
        self.duration_label.setObjectName("timeLabel")

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setObjectName("seekSlider")
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderPressed.connect(self._on_seek_pressed)
        self.seek_slider.sliderReleased.connect(self._on_seek_released)

        seek_row.addWidget(self.time_label)
        seek_row.addWidget(self.seek_slider, 1)
        seek_row.addWidget(self.duration_label)
        root.addLayout(seek_row)

        # ── Button row ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        btn_row.addStretch(1)

        # Shuffle (placeholder)
        self.shuffle_btn = IconButton("⇄", size=32, font_size=13)
        self.shuffle_btn.setToolTip("Karışık Çal")
        btn_row.addWidget(self.shuffle_btn)

        # 10s geri
        self.backward_btn = IconButton("⏮", size=36, font_size=16)
        self.backward_btn.setToolTip("10 saniye geri")
        self.backward_btn.clicked.connect(self.skip_backward.emit)
        btn_row.addWidget(self.backward_btn)

        # Prev
        self.prev_btn = IconButton("◀", size=36, font_size=14)
        self.prev_btn.setToolTip("Önceki")
        btn_row.addWidget(self.prev_btn)

        # Play / Pause
        self.play_btn = PlayButton()
        self.play_btn.clicked.connect(self._toggle_play)
        btn_row.addWidget(self.play_btn)

        # Next
        self.next_btn = IconButton("▶", size=36, font_size=14)
        self.next_btn.setToolTip("Sonraki")
        btn_row.addWidget(self.next_btn)

        # 10s ileri
        self.forward_btn = IconButton("⏭", size=36, font_size=16)
        self.forward_btn.setToolTip("10 saniye ileri")
        self.forward_btn.clicked.connect(self.skip_forward.emit)
        btn_row.addWidget(self.forward_btn)

        # Repeat (placeholder)
        self.repeat_btn = IconButton("🔁", size=32, font_size=13)
        self.repeat_btn.setToolTip("Tekrarla")
        btn_row.addWidget(self.repeat_btn)

        btn_row.addStretch(1)

        # ── Volume row (alt satır, sağda) ──
        vol_row = QHBoxLayout()
        vol_row.addStretch(1)

        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 13px;")
        vol_icon.setFixedWidth(20)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)

        vol_row.addWidget(vol_icon)
        vol_row.addWidget(self.volume_slider)

        root.addLayout(btn_row)
        root.addLayout(vol_row)

    def _toggle_play(self) -> None:
        self._is_playing = not self._is_playing
        self.play_btn.setText("⏸" if self._is_playing else "▶")
        (self.play_clicked if self._is_playing else self.pause_clicked).emit()

    def set_playing_state(self, playing: bool) -> None:
        self._is_playing = playing
        self.play_btn.setText("⏸" if playing else "▶")

    def _on_seek_pressed(self) -> None:
        self._user_seeking = True

    def _on_seek_released(self) -> None:
        self._user_seeking = False
        self.seek_requested.emit(self.seek_slider.value())

    def set_duration(self, ms: int) -> None:
        self.seek_slider.setRange(0, ms)
        self.duration_label.setText(_ms_to_mmss(ms))

    def set_position(self, ms: int) -> None:
        if not self._user_seeking:
            self.seek_slider.setValue(ms)
        self.time_label.setText(_ms_to_mmss(ms))
