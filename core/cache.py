import json
import hashlib
import os
from typing import Optional

from .lyrics_model import Song, Line, Word

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".lyricsync_cache")


def _ensure_cache_dir() -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)


def cache_path_for(audio_path: str) -> str:
    _ensure_cache_dir()
    h = hashlib.sha1(os.path.abspath(audio_path).encode("utf-8")).hexdigest()[:16]
    base = os.path.splitext(os.path.basename(audio_path))[0]
    return os.path.join(CACHE_DIR, f"{base}_{h}.json")


def save_song(song: Song, path: Optional[str] = None) -> str:
    path = path or cache_path_for(song.audio_path)
    data = {
        "audio_path": song.audio_path,
        "lines": [
            [{"text": w.text, "start": w.start, "end": w.end} for w in line.words]
            for line in song.lines
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_song(path: str) -> Song:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    lines = []
    for line_data in data["lines"]:
        words = [Word(text=w["text"], start=w["start"], end=w["end"]) for w in line_data]
        lines.append(Line(words=words))
    return Song(lines=lines, audio_path=data.get("audio_path", ""))


def has_cache(audio_path: str) -> bool:
    return os.path.exists(cache_path_for(audio_path))
