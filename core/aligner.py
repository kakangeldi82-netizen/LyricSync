"""
Düz şarkı sözünü, ses dosyasındaki gerçek zamanlamayla eşleştirir.

Akış:
1) faster-whisper ile şarkı transkribe edilir (word_timestamps=True) ->
   Whisper'ın DUYDUĞU kelimeler + zaman damgaları elde edilir.
2) Kullanıcının yazdığı GERÇEK sözlerle, Whisper'ın duyduğu kelimeler
   difflib.SequenceMatcher ile hizalanır (kelimeler farklı yazılsa/yanlış
   duyulsa bile sıralama korunduğu için iyi çalışır).
3) Eşleşmeyen (Whisper'ın kaçırdığı / fazladan duyduğu) kelimeler,
   komşu zaman damgaları arasında lineer interpolasyonla doldurulur.
"""

import re
import difflib
from typing import List, Optional, Callable

from .lyrics_model import Word, Line, Song

ProgressCB = Optional[Callable[[str], None]]


def normalize(w: str) -> str:
    return re.sub(r"[^\w']", "", w, flags=re.UNICODE).lower()


def parse_lyrics_text(text: str) -> List[Line]:
    lines = []
    for raw_line in text.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        words = [Word(text=w) for w in raw_line.split()]
        lines.append(Line(words=words))
    return lines


def transcribe_words(audio_path: str, model_size: str = "small",
                      language: Optional[str] = None,
                      progress_cb: ProgressCB = None) -> List[dict]:
    from faster_whisper import WhisperModel

    if progress_cb:
        progress_cb(f"Whisper modeli yükleniyor ({model_size})...")
    model = WhisperModel(model_size, device="auto", compute_type="int8")

    if progress_cb:
        progress_cb("Ses transkribe ediliyor...")
    segments, _info = model.transcribe(audio_path, word_timestamps=True, language=language)

    asr_words = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            token = (w.word or "").strip()
            if token:
                asr_words.append({"text": token, "start": w.start, "end": w.end})
    return asr_words


def align_lyrics_to_audio(audio_path: str, lyrics_text: str,
                           model_size: str = "small",
                           language: Optional[str] = None,
                           progress_cb: ProgressCB = None) -> Song:
    asr_words = transcribe_words(audio_path, model_size=model_size,
                                  language=language, progress_cb=progress_cb)

    lines = parse_lyrics_text(lyrics_text)
    flat_words = [w for line in lines for w in line.words]

    if not asr_words or not flat_words:
        return Song(lines=lines, audio_path=audio_path)

    if progress_cb:
        progress_cb("Kelimeler hizalanıyor...")

    asr_norm = [normalize(w["text"]) for w in asr_words]
    lyr_norm = [normalize(w.text) for w in flat_words]

    sm = difflib.SequenceMatcher(None, asr_norm, lyr_norm, autojunk=False)

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                asr_w = asr_words[i1 + k]
                lyr_w = flat_words[j1 + k]
                lyr_w.start = asr_w["start"]
                lyr_w.end = asr_w["end"]
        elif tag == "replace":
            n = min(i2 - i1, j2 - j1)
            for k in range(n):
                asr_w = asr_words[i1 + k]
                lyr_w = flat_words[j1 + k]
                lyr_w.start = asr_w["start"]
                lyr_w.end = asr_w["end"]
        # 'insert' / 'delete' -> zamanı olmayan kelimeler aşağıda dolduruluyor

    if progress_cb:
        progress_cb("Boşluklar dolduruluyor...")
    _interpolate_missing(flat_words)

    return Song(lines=lines, audio_path=audio_path)


def _interpolate_missing(flat_words: List[Word]) -> None:
    n = len(flat_words)
    i = 0
    while i < n:
        if flat_words[i].start is None:
            j = i
            while j < n and flat_words[j].start is None:
                j += 1

            prev_end = flat_words[i - 1].end if i > 0 and flat_words[i - 1].end is not None else 0.0
            gap = j - i

            if j < n and flat_words[j].start is not None:
                next_start = flat_words[j].start
            else:
                next_start = prev_end + 0.5 * (gap + 1)

            step = (next_start - prev_end) / (gap + 1) if gap > 0 else 0.3
            for k in range(gap):
                s = prev_end + step * (k + 1)
                e = prev_end + step * (k + 2)
                flat_words[i + k].start = s
                flat_words[i + k].end = e
            i = j
        else:
            i += 1
