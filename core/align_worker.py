from PyQt6.QtCore import QThread, pyqtSignal

from .aligner import align_lyrics_to_audio
from .lyrics_model import Song


class AlignWorker(QThread):
    progress = pyqtSignal(str)
    finished_ok = pyqtSignal(object)   # Song
    failed = pyqtSignal(str)

    def __init__(self, audio_path: str, lyrics_text: str, model_size: str = "small",
                 language: str | None = None):
        super().__init__()
        self.audio_path = audio_path
        self.lyrics_text = lyrics_text
        self.model_size = model_size
        self.language = language

    def run(self) -> None:
        try:
            song: Song = align_lyrics_to_audio(
                self.audio_path,
                self.lyrics_text,
                model_size=self.model_size,
                language=self.language,
                progress_cb=lambda msg: self.progress.emit(msg),
            )
            self.finished_ok.emit(song)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))
