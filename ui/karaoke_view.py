from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QScrollArea, QGraphicsOpacityEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, QVariantAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor, QPainter, QFont

from .flow_layout import FlowLayout
from core.lyrics_model import Song, Line

DIM_COLOR = QColor("#4a4a56")
SUNG_COLOR = QColor("#d7d7e0")
ACTIVE_COLOR = QColor("#ffffff")
ACTIVE_GLOW = QColor("#ffffff")


class WordLabel(QLabel):
    """Kelimeyi tek renkle değil; söylenme ilerlemesine göre soldan sağa
    dolan, beyaz + glow'lu bir 'wipe' efektiyle çizen özel etiket."""

    def __init__(self, text: str):
        super().__init__(text)
        self._state = "upcoming"  # upcoming | active | sung
        self._progress = 0.0      # 0..1, sadece state == active iken anlamlı

        font = QFont("Segoe UI Semibold", 20)
        font.setWeight(QFont.Weight.DemiBold)
        self.setFont(font)
        self.setStyleSheet("background: transparent; border: none;")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWordWrap(False)
        self.setContentsMargins(0, 0, 0, 0)

    def set_upcoming(self) -> None:
        if self._state == "upcoming":
            return
        self._state = "upcoming"
        self._progress = 0.0
        self.update()

    def set_sung(self) -> None:
        if self._state == "sung":
            return
        self._state = "sung"
        self._progress = 1.0
        self.update()

    def set_active(self, progress: float) -> None:
        progress = min(max(progress, 0.0), 1.0)
        self._state = "active"
        self._progress = progress
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt override)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        rect = self.rect()
        flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        text = self.text()

        if self._state == "sung":
            painter.setPen(SUNG_COLOR)
            painter.drawText(rect, flags, text)
        elif self._state == "upcoming":
            painter.setPen(DIM_COLOR)
            painter.drawText(rect, flags, text)
        else:
            # 1) tüm kelimeyi soluk renkte çiz (henüz söylenmemiş kısım)
            painter.setPen(DIM_COLOR)
            painter.drawText(rect, flags, text)

            fm = self.fontMetrics()
            text_width = fm.horizontalAdvance(text)
            fill_w = round(text_width * self._progress)
            if fill_w > 0:
                painter.save()
                # NOT: clip rect'i widget yüksekliğinin tamamını kaplıyor,
                # glow offsetleri clip dışına taşmasın diye biraz pay bırakıyoruz.
                clip_rect = QRect(rect.x(), rect.y() - 6, fill_w, rect.height() + 12)
                painter.setClipRect(clip_rect)

                # 2) yumuşak glow: aynı metni artan offsetle, azalan opaklıkla
                #    üst üste çizip bulanıklık hissi veriyoruz (arka plan bloğu
                #    OLUŞTURMAMASI için sadece pen rengi değişiyor, dolgu yok)
                glow = QColor(ACTIVE_GLOW)
                for radius, alpha in ((4, 35), (2, 70)):
                    glow.setAlpha(alpha)
                    painter.setPen(glow)
                    for dx, dy in ((-radius, 0), (radius, 0), (0, -radius), (0, radius)):
                        painter.drawText(rect.translated(dx, dy), flags, text)

                # 3) net beyaz metin, glow'un üstünde
                painter.setPen(ACTIVE_COLOR)
                painter.drawText(rect, flags, text)
                painter.restore()

            # 4) dolum sınırında keskin, parlak bir ışık çizgisi
            if 0 < fill_w < text_width:
                painter.save()
                edge_rect = QRect(rect.x() + fill_w - 1, rect.y() - 6, 2, rect.height() + 12)
                painter.setClipRect(edge_rect)
                painter.setPen(QColor(255, 255, 255, 235))
                painter.drawText(rect, flags, text)
                painter.restore()

        painter.end()


class LineWidget(QWidget):
    def __init__(self, line: Line):
        super().__init__()
        self.line = line
        self.word_labels: List[WordLabel] = []

        layout = FlowLayout(self, hspacing=11, vspacing=6)
        layout.setContentsMargins(0, 8, 0, 8)
        for w in line.words:
            lbl = WordLabel(w.text)
            self.word_labels.append(lbl)
            layout.addWidget(lbl)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.3)
        self.setGraphicsEffect(self._opacity_effect)

        self._opacity_anim = QVariantAnimation(self)
        self._opacity_anim.setDuration(260)
        self._opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._opacity_anim.valueChanged.connect(self._opacity_effect.setOpacity)

    def set_active(self, active: bool) -> None:
        target = 1.0 if active else 0.3
        self._opacity_anim.stop()
        self._opacity_anim.setStartValue(self._opacity_effect.opacity())
        self._opacity_anim.setEndValue(target)
        self._opacity_anim.start()


class KaraokeView(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.vlayout = QVBoxLayout(self.container)
        self.vlayout.setSpacing(20)
        self.vlayout.setContentsMargins(56, 90, 56, 90)
        self.vlayout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setWidget(self.container)

        self.line_widgets: List[LineWidget] = []
        self.song: Optional[Song] = None
        self.current_line_idx = -1

    def load_song(self, song: Song) -> None:
        for lw in self.line_widgets:
            lw.setParent(None)
        self.line_widgets = []
        self.song = song

        for line in song.lines:
            lw = LineWidget(line)
            self.vlayout.addWidget(lw, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.line_widgets.append(lw)
        self.current_line_idx = -1

    def update_time(self, t: float) -> None:
        if not self.song or not self.line_widgets:
            return

        active_idx = self._find_active_line(t)

        for idx, line_widget in enumerate(self.line_widgets):
            for w, lbl in zip(line_widget.line.words, line_widget.word_labels):
                if w.start is None:
                    continue
                w_start = w.start
                w_end = w.end if w.end is not None else w.start

                if t < w_start:
                    lbl.set_upcoming()
                elif t >= w_end:
                    lbl.set_sung()
                else:
                    duration = max(w_end - w_start, 0.001)
                    lbl.set_active((t - w_start) / duration)
            line_widget.set_active(idx == active_idx)

        if active_idx != self.current_line_idx:
            self.current_line_idx = active_idx
            self._scroll_to(active_idx)

    def _find_active_line(self, t: float) -> int:
        lines = self.song.lines
        for idx, line in enumerate(lines):
            if line.start is None:
                continue
            end = line.end if line.end is not None else line.start
            if line.start <= t <= end:
                return idx
        for idx, line in enumerate(lines):
            if line.start is not None and line.start > t:
                return max(0, idx - 1)
        return len(lines) - 1

    def _scroll_to(self, idx: int) -> None:
        if 0 <= idx < len(self.line_widgets):
            self.ensureWidgetVisible(self.line_widgets[idx], yMargin=190)