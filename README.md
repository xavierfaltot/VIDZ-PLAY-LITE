# VIDZ PLAY LITE

VIDZ PLAY LITE is the lightweight version of VIDZ PLAY: a single-file browser instrument for playing local video folders with automatic live mixing.

Repository: https://github.com/xavierfaltot/VIDZ-PLAY-LITE

This repository contains only the Lite version. It is made for fast setup, local playback, and a direct performance flow. Load a folder of videos, optionally load an audio file or use microphone input, then press play. The engine alternates clips, reacts to timing, applies visual blend/effect logic, and runs fully in the browser.

No server. No cloud upload. No bundled media.

The full version is available on demand.

## Features

- Local video folder import
- Optional machine media index for Raspberry Pi / kiosk mode
- Optional local audio file
- Optional microphone-reactive mode
- Fullscreen video stage
- Two hidden video decks for continuous playback
- Automatic clip switching
- Smart visual mixing and FX
- On-screen filters: ALL, FAST, SLOW, DARK, BRIGHT, WIDE, VERTICAL, SHORT, LONG, LOW, MED, HIGH
- Scene/energy-aware timing logic
- Local-only playback through the browser
- Mobile/touch-oriented interface

## Run

Open:

```text
index.html
```

Then:

1. Press `ADD VIDEO(S)`.
2. Select video files or a video folder.
3. Optionally add an audio file.
4. Press the central play control.

For best results, use Chrome or another Chromium browser because folder import uses browser file APIs.

## Raspberry Pi / Machine Mode

VIDZ PLAY LITE can also load a prepared `media-index.json` at startup. This is the recommended mode for a physical box with removable media cards.

Hardware blueprint:

```text
hardware/raspberry-pi-box.md
interface/low-tech-multi-screen-prompt.md
```

Machine I/O:

```text
VIDEO CARD / AUDIO CARD / EXPORT CARD / MIC / LINE IN / HDMI OUT / AUDIO OUT
```

Install `ffmpeg` on the Raspberry Pi:

```bash
sudo apt install ffmpeg
```

Scan the video and audio cards:

```bash
python3 tools/vidz_scan_lite.py \
  --video /media/VIDZ_VIDEO \
  --audio /media/VIDZ_AUDIO \
  --output media-index.json \
  --cache cache \
  --video-url /media/video \
  --audio-url /media/audio
```

The scanner creates:

```text
media-index.json
cache/thumbs/
```

The index stores file references, duration, size, orientation, brightness, motion, energy, cut points and thumbnail paths. It does not copy large video/audio files.

When `index.html` is served from the Raspberry Pi local web server, it automatically reads `media-index.json` if present. The player then opens with the scanned library ready to filter and play.

## Scan And Filtr

VIDZ PLAY LITE can now be used as separate blocks that can be chained:

```text
SCAN -> FILTR -> PLAY
```

Block definitions live in:

```text
blocks/
```

`SCAN` is the preparation block:

```bash
python3 tools/vidz_scan_lite.py --video /path/to/videos --output media-index.json
```

`FILTR` is the organisation block. It filters, sorts, and can prepare an export card.

Command-line filtr example:

```bash
python3 tools/vidz_filtr_lite.py \
  --input media-index.json \
  --output media-index.filtr.json \
  --energy high \
  --sort energy \
  --reverse
```

Export card example:

```bash
python3 tools/vidz_filtr_lite.py \
  --input media-index.json \
  --set-name NIGHT_SET_01 \
  --export-dir /media/VIDZ_EXPORT_CARD \
  --copy-media \
  --copy-thumbs \
  --organise-by energy
```

On-screen filters:

```text
ALL / FAST / SLOW / DARK / BRIGHT / WIDE / VERTICAL / SHORT / LONG / LOW / MED / HIGH
```

Filters use the scanner metadata when available. If no index exists, VIDZ PLAY LITE still works with the normal browser file picker and derives basic tags from filenames and video metadata.

To play a filtered set, put the FILTR JSON next to `index.html` as:

```text
media-index.json
```

## GitHub Pages

This repository is ready for GitHub Pages.

Use:

```text
Settings -> Pages -> Deploy from branch -> main -> /root
```

The public entry point is:

```text
index.html
```

## Files

```text
index.html
assets/vidz-play-lite-logo.png
blocks/
hardware/
tools/vidz_scan_lite.py
tools/vidz_filtr_lite.py
README.md
LICENSE
.gitignore
```

## Privacy

VIDZ PLAY LITE reads local files through the browser file picker. Videos and audio are not uploaded by the app.

Microphone input, when enabled, is used locally for reactive playback only.

## Notes

This is a live-playback instrument, not an editing timeline. It is designed for quick visual sets, tests, demos, and lightweight performance situations where opening a folder and playing immediately matters more than building a full project.

The full version of VIDZ PLAY is available on demand for expanded controls and dedicated performance setups.
