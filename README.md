# 🎤 LyricSync

**Local, desktop karaoke lyrics application.** Input a song alongside plain (timestamp-free) lyrics text, and it uses Whisper-based local audio analysis to detect when every word is spoken—displaying them with Spotify/YouTube Music style word-by-word highlight animations.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Settings & Customization](#settings--customization)
- [Project Structure](#project-structure)

---

## How It Works

1. **AI Audio Analysis:** `faster-whisper` transcribes the track and extracts word-level timestamps.
2. **Smart Sequence Matching:** The words *heard* by Whisper (even if misheard) are matched sequentially against your *actual* provided lyrics using `difflib`—transferring precise timing to your correct text.
3. **Smooth Interpolation:** Unmatched gaps or silent periods are filled using mathematical interpolation between neighboring timestamps.
4. **Local Caching:** Results are saved as JSON files in `~/.lyricsync_cache/`. Opening the same song again loads instantly without needing re-analysis.

---

## Installation

### 1. Prerequisites

`faster-whisper` requires **FFmpeg** installed on your system for audio processing:

- **Windows:** `winget install ffmpeg` (or add to your system `PATH`)
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

### 2. Getting the Code

You can either clone the repository using Git or download it as a ZIP archive:

#### **Option A: Clone with Git (Recommended)**
```bash
git clone [https://github.com/your-username/lyricsync.git](https://github.com/your-username/lyricsync.git)
cd lyricsync
Option B: Download ZIP
Click the green Code button on GitHub and select Download ZIP.

Extract the archive to your desired location.

Open your terminal/command prompt and navigate into the extracted folder:

Bash
cd path/to/lyricsync
3. Setup Virtual Environment
Bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
Note: On first launch, the Whisper model (small, ~500MB) will automatically be downloaded to ~/.cache/huggingface. An internet connection is required for this step; subsequent runs operate completely offline locally.

How to Run
Bash
python main.py
Workflow:
🎵 Open Song — Select an audio file (.mp3, .wav, .m4a, .flac, .ogg).

📝 Enter Lyrics — Paste the plain text line-by-line (no timestamps needed, they will be auto-generated).

✨ Align — Click to let Whisper analyze the track (takes 10–60 seconds on CPU depending on song duration).

▶️ Play — Enjoy word-by-word animated highlights as the active line automatically centers itself.

Settings & Customization
Speed/Accuracy Balance: Modify model_size in core/aligner.py ("tiny", "base", "small", "medium", "large-v3"). If you have a supported GPU, set device="cuda" for drastic speed improvements.

Custom Themes: Customize text colors (ACTIVE_COLOR, SUNG_COLOR, DIM_COLOR) inside ui/karaoke_view.py.

Cache Management: To reset or re-align a song, simply delete its corresponding .json file inside the ~/.lyricsync_cache/ directory and click Align again in the application.

Project Structure
Plaintext
lyricsync/
├── main.py             # Entry point, connects all UI components
├── core/
│   ├── lyrics_model.py # Data structures for Word / Line / Song models
│   ├── aligner.py      # Whisper + difflib alignment engine
│   ├── align_worker.py # Executes alignment tasks off the UI thread (QThread)
│   └── cache.py        # Handles JSON caching of aligned song data
└── ui/
    ├── main_window.py  # Main window interface
    ├── karaoke_view.py # Word-by-word highlights & auto-scroll viewport
    ├── controls.py     # Play/pause, seeking, and volume controls
    ├── lyrics_dialog.py# Plain text lyrics input modal
    ├── flow_layout.py  # Flow layout manager for arranging word elements
    └── styles.py       # Dark theme & glassmorphism QSS styling
