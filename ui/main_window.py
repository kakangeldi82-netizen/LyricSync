import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from core import cache
from core.align_worker import AlignWorker
from .karaoke_view import KaraokeView
from .controls import Controls
from .lyrics_dialog import LyricsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LyricSync — Lokal Karaoke Sözleri")
        self.resize(900, 640)

        self.audio_path: str | None = None
        self.pending_lyrics_text: str = ""
        self.align_worker: AlignWorker | None = None
        self.progress_dialog: QProgressDialog | None = None

        # --- Medya oynatıcı ---
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

        # Kelime "wipe" animasyonunun akıcı olması için positionChanged'den
        # bağımsız, yüksek sıklıkta (~30fps) tik atan zamanlayıcı.
        self.smooth_timer = QTimer(self)
        self.smooth_timer.setInterval(33)
        self.smooth_timer.timeout.connect(self._on_smooth_tick)

        # --- Üst bar ---
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 14, 20, 14)

        self.song_title_label = QLabel("Şarkı yüklenmedi")
        self.song_title_label.setObjectName("songTitle")

        self.open_audio_btn = QPushButton("🎵 Şarkı Aç")
        self.open_audio_btn.setObjectName("openAudioButton")
        self.open_audio_btn.clicked.connect(self._on_open_audio)

        self.open_lyrics_btn = QPushButton("📝 Sözleri Gir")
        self.open_lyrics_btn.setObjectName("openLyricsButton")
        self.open_lyrics_btn.clicked.connect(self._on_open_lyrics)
        self.open_lyrics_btn.setEnabled(False)

        self.align_btn = QPushButton("✨ Hizala")
        self.align_btn.setObjectName("alignButton")
        self.align_btn.clicked.connect(self._on_align)
        self.align_btn.setEnabled(False)

        left_box = QVBoxLayout()
        left_box.addWidget(self.song_title_label)
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        left_box.addWidget(self.status_label)

        top_layout.addLayout(left_box, 1)
        top_layout.addWidget(self.open_audio_btn)
        top_layout.addWidget(self.open_lyrics_btn)
        top_layout.addWidget(self.align_btn)

        # --- Karaoke görünümü ---
        self.karaoke_view = KaraokeView()

        # --- Alt kontrol bar ---
        self.controls = Controls()
        self.controls.play_clicked.connect(self.player.play)
        self.controls.pause_clicked.connect(self.player.pause)
        self.controls.seek_requested.connect(self.player.setPosition)
        self.controls.skip_backward.connect(self._skip_backward)
        self.controls.skip_forward.connect(self._skip_forward)
        self.controls.volume_changed.connect(
            lambda v: self.audio_output.setVolume(v / 100.0)
        )

        central = QWidget()
        self.controls.skip_forward.connect(self._skip_forward)
        self.controls.volume_changed.connect(
            lambda v: self.audio_output.setVolume(v / 100.0)
        )
        self.controls.play_clicked.connect(self.player.play)
        self.controls.pause_clicked.connect(self.player.pause)
        self.controls.seek_requested.connect(self.player.setPosition)
        self.controls.volume_changed.connect(
            lambda v: self.audio_output.setVolume(v / 100.0)
        )

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(top_bar)
        root.addWidget(self.karaoke_view, 1)
        root.addWidget(self.controls)
        self.setCentralWidget(central)

    # ---------- Dosya işlemleri ----------

    def _on_open_audio(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Şarkı Seç", "", "Ses Dosyaları (*.mp3 *.wav *.m4a *.flac *.ogg)"
        )
        if not path:
            return
        self.audio_path = path
        self.song_title_label.setText(os.path.basename(path))
        self.player.setSource(QUrl.fromLocalFile(path))
        self.open_lyrics_btn.setEnabled(True)

        if cache.has_cache(path):
            self.status_label.setText("Bu şarkı için kayıtlı hizalama bulundu, yükleniyor...")
            song = cache.load_song(cache.cache_path_for(path))
            self.karaoke_view.load_song(song)
            self.status_label.setText("Hazır (önbellekten yüklendi).")
        else:
            self.status_label.setText("Şimdi sözleri girip 'Hizala'ya bas.")

    def _on_open_lyrics(self) -> None:
        dlg = LyricsDialog(self, initial_text=self.pending_lyrics_text)
        if dlg.exec():
            self.pending_lyrics_text = dlg.get_text().strip()
            self.align_btn.setEnabled(bool(self.pending_lyrics_text))
            self.status_label.setText("Sözler alındı. 'Hizala'ya basabilirsin.")

    # ---------- Hizalama ----------

    def _on_align(self) -> None:
        if not self.audio_path or not self.pending_lyrics_text:
            return

        self.progress_dialog = QProgressDialog("Hizalanıyor...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Lütfen bekleyin")
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.show()

        self.align_worker = AlignWorker(self.audio_path, self.pending_lyrics_text)
        self.align_worker.progress.connect(self._on_align_progress)
        self.align_worker.finished_ok.connect(self._on_align_finished)
        self.align_worker.failed.connect(self._on_align_failed)
        self.align_worker.start()

    def _on_align_progress(self, msg: str) -> None:
        if self.progress_dialog:
            self.progress_dialog.setLabelText(msg)
        self.status_label.setText(msg)

    def _on_align_finished(self, song) -> None:
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        self.karaoke_view.load_song(song)
        cache.save_song(song)
        self.status_label.setText("Hizalama tamamlandı. Oynatabilirsin.")

    def _on_align_failed(self, error: str) -> None:
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        self.status_label.setText("Hizalama başarısız.")
        QMessageBox.critical(self, "Hata", f"Hizalama sırasında hata oluştu:\n{error}")

    # ---------- Oynatıcı sinyalleri ----------

    def _on_position_changed(self, ms: int) -> None:
        self.controls.set_position(ms)
        self.karaoke_view.update_time(ms / 1000.0)

    def _on_duration_changed(self, ms: int) -> None:
        self.controls.set_duration(ms)

    def _on_playback_state_changed(self, state) -> None:
        is_playing = state == QMediaPlayer.PlaybackState.PlayingState
        self.controls.set_playing_state(is_playing)
        if is_playing:
            self.smooth_timer.start()
        else:
            self.smooth_timer.stop()

    def _on_smooth_tick(self) -> None:
        self.karaoke_view.update_time(self.player.position() / 1000.0)

    def _skip_backward(self) -> None:
        new_pos = max(0, self.player.position() - 10_000)
        self.player.setPosition(new_pos)

    def _skip_forward(self) -> None:
        new_pos = min(self.player.duration(), self.player.position() + 10_000)
        self.player.setPosition(new_pos)
        self.karaoke_view.update_time(self.player.position() / 1000.0)
