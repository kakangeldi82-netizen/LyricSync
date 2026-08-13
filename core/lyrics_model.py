from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Word:
    text: str
    start: Optional[float] = None  # saniye
    end: Optional[float] = None


@dataclass
class Line:
    words: List[Word] = field(default_factory=list)

    @property
    def start(self) -> Optional[float]:
        for w in self.words:
            if w.start is not None:
                return w.start
        return None

    @property
    def end(self) -> Optional[float]:
        for w in reversed(self.words):
            if w.end is not None:
                return w.end
        return None

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)


@dataclass
class Song:
    lines: List[Line] = field(default_factory=list)
    audio_path: str = ""
