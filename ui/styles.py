STYLE_SHEET = """
/* ═══════════════════════════════════════════════════════
   LyricSync — Soft Dark Theme (Spotify / Apple Music inspired)
   ═══════════════════════════════════════════════════════ */

QWidget {
    background-color: #121212;
    font-family: "Segoe UI", "SF Pro Display", "Inter", sans-serif;
    color: #ffffff;
}

QMainWindow {
    background-color: #121212;
}

/* ── Üst Bar ── */
#topBar {
    background-color: rgba(255, 255, 255, 8);
    border-bottom: 1px solid rgba(255, 255, 255, 10);
}

#openAudioButton, #openLyricsButton, #alignButton {
    background-color: rgba(255, 255, 255, 14);
    color: #f0f0f5;
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 600;
}
#openAudioButton:hover, #openLyricsButton:hover, #alignButton:hover {
    background-color: rgba(29, 185, 84, 35);
    border: 1px solid rgba(29, 185, 84, 70);
    color: #ffffff;
}
#openAudioButton:pressed, #openLyricsButton:pressed, #alignButton:pressed {
    background-color: rgba(29, 185, 84, 50);
}

#songTitle {
    color: #ffffff;
    font-size: 15px;
    font-weight: 600;
}
#statusLabel {
    color: #a0a0a0;
    font-size: 12px;
}

/* ── Zaman Etiketleri ── */
#timeLabel {
    color: #a7a7a7;
    font-size: 11px;
    font-weight: 500;
    min-width: 38px;
    qproperty-alignment: AlignCenter;
}

/* ── Seek Slider (Ana İlerleme) ── */
QSlider#seekSlider::groove:horizontal {
    height: 4px;
    background: rgba(255, 255, 255, 25);
    border-radius: 2px;
}
QSlider#seekSlider::sub-page:horizontal {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #1db954,
        stop:1 #1ed760
    );
    border-radius: 2px;
}
QSlider#seekSlider::handle:horizontal {
    background: #ffffff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
    border: none;
}
QSlider#seekSlider::handle:horizontal:hover {
    background: #1db954;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

/* ── Volume Slider ── */
QSlider#volumeSlider::groove:horizontal {
    height: 4px;
    background: rgba(255, 255, 255, 25);
    border-radius: 2px;
}
QSlider#volumeSlider::sub-page:horizontal {
    background: #a7a7a7;
    border-radius: 2px;
}
QSlider#volumeSlider::handle:horizontal {
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
    border: none;
}
QSlider#volumeSlider::handle:horizontal:hover {
    background: #1db954;
}

/* ── ScrollBar ── */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 35);
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 55);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* ── QDialog (Şarkı Sözleri Gir) ── */
QDialog {
    background-color: #181818;
    border-radius: 12px;
}
QDialog QLabel {
    color: #e0e0e0;
    font-size: 13px;
    padding-bottom: 4px;
}
QDialog QTextEdit {
    background-color: #242424;
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 12);
    border-radius: 8px;
    padding: 10px;
    font-size: 14px;
    selection-background-color: #1db954;
}
QDialog QTextEdit:focus {
    border: 1px solid rgba(29, 185, 84, 60);
}
QDialog QPushButton {
    background-color: rgba(255, 255, 255, 14);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
}
QDialog QPushButton:hover {
    background-color: rgba(29, 185, 84, 35);
    border: 1px solid rgba(29, 185, 84, 70);
}

/* ── Progress Dialog ── */
QProgressDialog {
    background-color: #181818;
    color: #ffffff;
}
QProgressDialog QLabel {
    color: #e0e0e0;
    font-size: 13px;
}
"""
